"""
Q&A System with Retrieval-Augmented Generation (RAG)
Allows users to ask questions about documents in the data room
"""
from typing import List, Dict, Any, Optional
import structlog
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec
import tiktoken

from api.config import settings

logger = structlog.get_logger()


class DocumentQASystem:
    """
    Q&A system for querying DD documents
    Uses RAG architecture with vector database
    """

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )

        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Initialize Pinecone
        self.pc = None
        self.index = None
        self.vector_store = None
        self._initialize_vector_db()

        # QA prompt template
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert renewable energy transaction advisor assisting with due diligence.
            Answer questions based ONLY on the provided context from the data room documents.

            Guidelines:
            1. Provide accurate, specific answers citing document sources
            2. If information is not in the context, clearly state that
            3. Highlight any risks, red flags, or important considerations
            4. Use technical terminology appropriately
            5. Provide quantitative data when available
            6. Cross-reference information across documents when relevant

            Context from documents:
            {context}
            """),
            ("user", "{question}")
        ])

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            encoding = tiktoken.encoding_for_model(settings.LLM_MODEL)
            return len(encoding.encode(text))
        except Exception:
            # Fallback to approximate count
            return len(text) // 4

    def _initialize_vector_db(self):
        """Initialize vector database connection"""
        try:
            if settings.VECTOR_DB_TYPE == "pinecone" and settings.PINECONE_API_KEY:
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

                # Create index if it doesn't exist
                index_name = settings.PINECONE_INDEX_NAME
                if index_name not in self.pc.list_indexes().names():
                    self.pc.create_index(
                        name=index_name,
                        dimension=3072,  # text-embedding-3-large dimension
                        metric='cosine',
                        spec=ServerlessSpec(
                            cloud='aws',
                            region='us-east-1'
                        )
                    )
                    logger.info(f"Created Pinecone index: {index_name}")

                self.index = self.pc.Index(index_name)
                logger.info("Pinecone vector database initialized")

        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            # Fallback to in-memory ChromaDB or continue without vector store
            logger.warning("Continuing without persistent vector storage")

    async def index_document(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Index a document for Q&A

        Args:
            document_id: Unique document identifier
            text: Document text content
            metadata: Document metadata (filename, type, category, etc.)

        Returns:
            Number of chunks indexed
        """
        try:
            # Split document into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Create Document objects with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    **metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                documents.append(
                    Document(page_content=chunk, metadata=doc_metadata)
                )

            # Index in vector store
            if self.vector_store:
                await self.vector_store.aadd_documents(documents)
            elif self.index:
                # Direct Pinecone indexing
                embeddings_list = []
                for doc in documents:
                    embedding = await self.embeddings.aembed_query(doc.page_content)
                    embeddings_list.append({
                        "id": f"{document_id}_{doc.metadata['chunk_index']}",
                        "values": embedding,
                        "metadata": {
                            **doc.metadata,
                            "text": doc.page_content
                        }
                    })

                # Upsert in batches
                batch_size = 100
                for i in range(0, len(embeddings_list), batch_size):
                    batch = embeddings_list[i:i + batch_size]
                    self.index.upsert(vectors=batch)

                logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")

            return len(chunks)

        except Exception as e:
            logger.error(f"Failed to index document: {str(e)}")
            raise

    async def delete_document_index(self, document_id: str):
        """
        Delete document from index

        Args:
            document_id: Document identifier to delete
        """
        try:
            if self.index:
                # Delete all chunks for this document
                self.index.delete(filter={"document_id": document_id})
                logger.info(f"Deleted index for document {document_id}")

        except Exception as e:
            logger.error(f"Failed to delete document index: {str(e)}")

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query

        Args:
            query: User query
            top_k: Number of chunks to retrieve
            filter_metadata: Optional metadata filters

        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)

            # Query vector database
            if self.index:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                    filter=filter_metadata
                )

                chunks = []
                for match in results.matches:
                    chunks.append({
                        "text": match.metadata.get("text", ""),
                        "score": match.score,
                        "metadata": {
                            k: v for k, v in match.metadata.items()
                            if k != "text"
                        }
                    })

                return chunks

        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {str(e)}")
            return []

    async def answer_question(
        self,
        question: str,
        project_id: Optional[str] = None,
        document_types: Optional[List[str]] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG

        Args:
            question: User question
            project_id: Optional project ID to filter documents
            document_types: Optional list of document types to search
            max_sources: Maximum number of source documents to use

        Returns:
            Answer with sources and metadata
        """
        try:
            # Build filter
            filter_metadata = {}
            if project_id:
                filter_metadata["project_id"] = project_id
            if document_types:
                filter_metadata["document_type"] = {"$in": document_types}

            # Retrieve relevant chunks
            chunks = await self.retrieve_relevant_chunks(
                query=question,
                top_k=max_sources * 2,  # Get more chunks, then filter
                filter_metadata=filter_metadata if filter_metadata else None
            )

            if not chunks:
                return {
                    "answer": "I don't have enough information in the data room to answer this question. Please ensure the relevant documents have been uploaded and indexed.",
                    "sources": [],
                    "confidence": 0.0
                }

            # Prepare context from chunks
            context_parts = []
            sources = []

            for i, chunk in enumerate(chunks[:max_sources]):
                metadata = chunk["metadata"]
                context_parts.append(
                    f"[Source {i+1}: {metadata.get('filename', 'Unknown')} - {metadata.get('document_type', 'Unknown')}]\n"
                    f"{chunk['text']}\n"
                )

                sources.append({
                    "document_id": metadata.get("document_id"),
                    "filename": metadata.get("filename"),
                    "document_type": metadata.get("document_type"),
                    "relevance_score": round(chunk["score"], 3)
                })

            context = "\n\n".join(context_parts)

            # Generate answer using LLM
            messages = self.qa_prompt.format_messages(
                context=context,
                question=question
            )

            response = await self.llm.ainvoke(messages)
            answer = response.content

            # Calculate confidence based on relevance scores
            avg_relevance = sum(s["relevance_score"] for s in sources) / len(sources) if sources else 0
            confidence = min(avg_relevance * 1.2, 1.0)  # Scale up slightly, cap at 1.0

            logger.info(
                "Question answered",
                question=question[:100],
                num_sources=len(sources),
                confidence=confidence
            )

            return {
                "answer": answer,
                "sources": sources,
                "confidence": round(confidence, 3),
                "question": question
            }

        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }

    async def compare_documents(
        self,
        question: str,
        document_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare terms across multiple specific documents

        Args:
            question: Comparison question
            document_ids: List of document IDs to compare

        Returns:
            Comparison analysis
        """
        try:
            # Retrieve chunks from each document
            all_chunks = []
            for doc_id in document_ids:
                chunks = await self.retrieve_relevant_chunks(
                    query=question,
                    top_k=3,
                    filter_metadata={"document_id": doc_id}
                )
                all_chunks.extend(chunks)

            if not all_chunks:
                return {
                    "answer": "Unable to retrieve information from the specified documents for comparison.",
                    "sources": []
                }

            # Group chunks by document
            chunks_by_doc = {}
            for chunk in all_chunks:
                doc_id = chunk["metadata"]["document_id"]
                if doc_id not in chunks_by_doc:
                    chunks_by_doc[doc_id] = []
                chunks_by_doc[doc_id].append(chunk)

            # Create comparison prompt
            comparison_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are comparing terms across multiple renewable energy transaction documents.
                Provide a side-by-side comparison highlighting:
                1. Similarities in terms
                2. Differences and discrepancies
                3. Any conflicts or inconsistencies
                4. Which document has more favorable terms

                Documents to compare:
                {context}
                """),
                ("user", "Compare these documents regarding: {question}")
            ])

            # Build context
            context_parts = []
            for doc_id, chunks in chunks_by_doc.items():
                doc_context = "\n".join([c["text"] for c in chunks[:2]])
                filename = chunks[0]["metadata"].get("filename", doc_id)
                context_parts.append(f"Document: {filename}\n{doc_context}\n")

            context = "\n---\n".join(context_parts)

            # Generate comparison
            messages = comparison_prompt.format_messages(
                context=context,
                question=question
            )

            response = await self.llm.ainvoke(messages)

            return {
                "answer": response.content,
                "sources": [
                    {
                        "document_id": doc_id,
                        "filename": chunks[0]["metadata"].get("filename"),
                        "document_type": chunks[0]["metadata"].get("document_type")
                    }
                    for doc_id, chunks in chunks_by_doc.items()
                ],
                "comparison_type": "multi_document"
            }

        except Exception as e:
            logger.error(f"Document comparison failed: {str(e)}")
            return {
                "answer": f"Comparison failed: {str(e)}",
                "sources": []
            }


# Global QA system instance
qa_system = DocumentQASystem()

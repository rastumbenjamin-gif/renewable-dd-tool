/**
 * Chat Interface Component
 * Q&A interface for querying DD documents
 */
import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, FileText, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    document_id: string;
    filename: string;
    document_type: string;
    relevance_score: number;
  }>;
  confidence?: number;
  timestamp: Date;
}

interface ChatInterfaceProps {
  projectId: string;
  onAskQuestion: (question: string) => Promise<any>;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ projectId, onAskQuestion }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `Hello! I'm your DD assistant. I can help you with questions about the documents in this data room.

**I can help you:**
- Find specific terms in contracts (e.g., "What is the PPA price?")
- Compare documents (e.g., "Compare warranty terms across equipment contracts")
- Check compliance status (e.g., "Are all environmental permits in place?")
- Explain technical concepts (e.g., "Explain the interconnection queue position")
- Identify risks (e.g., "What are the key risks in this transaction?")

Ask me anything about the project!`,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await onAskQuestion(inputValue);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'bg-gray-100 text-gray-700';
    if (confidence >= 0.8) return 'bg-green-100 text-green-700';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">Document Q&A</h2>
        <p className="text-sm text-gray-600 mt-1">
          Ask questions about the documents in this data room
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white rounded-lg px-4 py-3'
                  : 'bg-gray-100 text-gray-900 rounded-lg px-4 py-3'
              }`}
            >
              {message.type === 'assistant' ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{message.content}</ReactMarkdown>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-300">
                      <div className="flex items-center space-x-2 mb-2">
                        <FileText className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-semibold text-gray-700">Sources:</span>
                      </div>
                      <div className="space-y-2">
                        {message.sources.map((source, idx) => (
                          <div
                            key={idx}
                            className="text-xs bg-white rounded p-2 border border-gray-200"
                          >
                            <div className="font-medium text-gray-900">{source.filename}</div>
                            <div className="text-gray-600 mt-1">
                              Type: {source.document_type} | Relevance:{' '}
                              {(source.relevance_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Confidence Score */}
                  {message.confidence !== undefined && (
                    <div className="mt-3 flex items-center space-x-2">
                      <span
                        className={`text-xs px-2 py-1 rounded ${getConfidenceColor(
                          message.confidence
                        )}`}
                      >
                        Confidence: {(message.confidence * 100).toFixed(0)}%
                      </span>
                      {message.confidence < 0.7 && (
                        <div className="flex items-center space-x-1 text-xs text-yellow-600">
                          <AlertCircle className="w-3 h-3" />
                          <span>Low confidence - verify with source documents</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}

              <div
                className={`text-xs mt-2 ${
                  message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span className="text-gray-600">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex items-end space-x-2">
          <div className="flex-1">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the documents..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Send</span>
              </>
            )}
          </button>
        </div>

        {/* Example Questions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-xs text-gray-600">Try asking:</span>
          {[
            'What is the PPA price?',
            'Summarize interconnection status',
            'What are the key risks?',
          ].map((example) => (
            <button
              key={example}
              onClick={() => setInputValue(example)}
              className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

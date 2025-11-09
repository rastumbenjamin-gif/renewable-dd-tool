/**
 * Project Context - Shared state for project data
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface Document {
  id: string;
  filename: string;
  document_type: string;
  category: string;
  upload_date: string;
  size_bytes: number;
  status: string;
}

interface ProjectContextType {
  projectId: string;
  documents: Document[];
  isLoading: boolean;
  refreshDocuments: () => Promise<void>;
  addDocument: (doc: Document) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};

interface ProjectProviderProps {
  children: ReactNode;
  projectId: string;
}

export const ProjectProvider: React.FC<ProjectProviderProps> = ({ children, projectId }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const refreshDocuments = async () => {
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/documents?project_id=${projectId}`);

      if (response.ok) {
        const docs = await response.json();
        setDocuments(docs);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addDocument = (doc: Document) => {
    setDocuments(prev => [...prev, doc]);
  };

  // Fetch documents on mount
  useEffect(() => {
    refreshDocuments();
  }, [projectId]);

  return (
    <ProjectContext.Provider
      value={{
        projectId,
        documents,
        isLoading,
        refreshDocuments,
        addDocument,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};

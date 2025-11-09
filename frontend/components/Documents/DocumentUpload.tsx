/**
 * Document Upload Component
 * Allows users to upload documents with drag & drop
 */
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle, AlertCircle, Loader2, X, FileText } from 'lucide-react';
import { useProject } from '../../contexts/ProjectContext';

interface DocumentUploadProps {
  projectId: string;
  onUploadComplete?: (document: any) => void;
}

interface UploadedFile {
  id: string;
  filename: string;
  status: 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ projectId, onUploadComplete }) => {
  const { documents, refreshDocuments, addDocument } = useProject();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [category, setCategory] = useState('Technical');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const fileId = Math.random().toString(36).substring(7);

      // Add file to state
      setUploadedFiles(prev => [...prev, {
        id: fileId,
        filename: file.name,
        status: 'uploading',
        progress: 0,
      }]);

      try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', projectId);
        formData.append('category', category);

        // Upload file
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/documents/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();

        // Update file status to success
        setUploadedFiles(prev => prev.map(f =>
          f.id === fileId
            ? { ...f, status: 'success', progress: 100 }
            : f
        ));

        // Add to global documents list
        addDocument(result);

        if (onUploadComplete) {
          onUploadComplete(result);
        }

      } catch (error) {
        console.error('Upload error:', error);
        setUploadedFiles(prev => prev.map(f =>
          f.id === fileId
            ? { ...f, status: 'error', error: error instanceof Error ? error.message : 'Upload failed' }
            : f
        ));
      }
    }
  }, [projectId, category, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
  });

  return (
    <div className="space-y-6">
      {/* Category Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Document Category
        </label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="Technical">Technical</option>
          <option value="Commercial">Commercial</option>
          <option value="Financial">Financial</option>
          <option value="Legal">Legal</option>
          <option value="Environmental">Environmental</option>
        </select>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        {isDragActive ? (
          <p className="text-lg text-blue-600">Drop the files here...</p>
        ) : (
          <>
            <p className="text-lg text-gray-700 mb-2">
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supported formats: PDF, DOCX, DOC, TXT, CSV
            </p>
          </>
        )}
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">Uploaded Files</h3>
          {uploadedFiles.map((file) => (
            <div
              key={file.id}
              className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
            >
              <div className="flex items-center space-x-3 flex-1">
                <File className="w-5 h-5 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.filename}
                  </p>
                  {file.error && (
                    <p className="text-xs text-red-600 mt-1">{file.error}</p>
                  )}
                </div>
              </div>

              <div className="ml-4">
                {file.status === 'uploading' && (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                )}
                {file.status === 'success' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
                {file.status === 'error' && (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* All Documents in Project */}
      {documents.length > 0 && (
        <div className="space-y-3 mt-8">
          <h3 className="text-lg font-semibold text-gray-900">All Project Documents ({documents.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-start justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-start space-x-3 flex-1">
                  <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {doc.filename}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {doc.category}
                      </span>
                      <span className="text-xs text-gray-500">
                        {(doc.size_bytes / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  </div>
                </div>
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;

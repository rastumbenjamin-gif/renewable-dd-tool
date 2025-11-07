/**
 * Dashboard Page - Renewable Energy DD Tool
 * Main dashboard with DD progress and Q&A interface
 */
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import DDProgressOverview from '../components/Dashboard/DDProgressOverview';
import ChatInterface from '../components/QA/ChatInterface';
import DocumentUpload from '../components/Documents/DocumentUpload';
import { ProjectProvider, useProject } from '../contexts/ProjectContext';
import { FileText, MessageSquare, Upload, LogOut } from 'lucide-react';

interface DDProgressData {
  total_items: number;
  completed_items: number;
  completion_percentage: number;
  by_category: {
    [key: string]: {
      total: number;
      completed: number;
    };
  };
}

function DashboardContent() {
  const router = useRouter();
  const { documents } = useProject();
  const [activeTab, setActiveTab] = useState<'overview' | 'qa' | 'documents'>('overview');
  const [progressData, setProgressData] = useState<DDProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const projectId = 'demo-project';

  // Fetch DD progress data
  useEffect(() => {
    fetchProgressData();
  }, []);

  // Refresh progress when documents change
  useEffect(() => {
    if (documents.length > 0) {
      fetchProgressData();
    }
  }, [documents.length]);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/dashboard/dd-progress/${projectId}`);

      if (!response.ok) {
        throw new Error('Failed to fetch progress data');
      }

      const data = await response.json();
      setProgressData(data);
    } catch (error) {
      console.error('Error fetching progress data:', error);
      // If no documents yet, show empty state
      setProgressData({
        total_items: 0,
        completed_items: 0,
        completion_percentage: 0,
        by_category: {},
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async (question: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/qa/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      return await response.json();
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  };

  const handleLogout = () => {
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Renewable Energy DD Tool
              </h1>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FileText className="w-5 h-5" />
              <span>DD Progress</span>
            </button>
            <button
              onClick={() => setActiveTab('qa')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'qa'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              <span>Q&A Assistant</span>
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'documents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Upload className="w-5 h-5" />
              <span>Documents</span>
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div>
            {progressData && (
              <DDProgressOverview data={progressData} loading={loading} />
            )}

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Documents Uploaded</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{documents.length}</p>
                  </div>
                  <FileText className="w-12 h-12 text-blue-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Categories</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {progressData ? Object.keys(progressData.by_category).length : 0}
                    </p>
                  </div>
                  <MessageSquare className="w-12 h-12 text-green-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Completion</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {progressData ? Math.round(progressData.completion_percentage) : 0}%
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">✓</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'qa' && (
          <div className="h-[calc(100vh-16rem)]">
            <ChatInterface projectId={projectId} onAskQuestion={handleAskQuestion} />
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Document Management</h2>
            <DocumentUpload
              projectId={projectId}
              onUploadComplete={(doc) => {
                console.log('Document uploaded:', doc);
                // You could refresh the document list here
              }}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default function Dashboard() {
  return (
    <ProjectProvider projectId="demo-project">
      <DashboardContent />
    </ProjectProvider>
  );
}

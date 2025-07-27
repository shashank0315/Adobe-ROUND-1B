import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [collections, setCollections] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analysisRequest, setAnalysisRequest] = useState({
    challenge_info: {
      challenge_id: 'round_1b_001',
      test_case_name: 'custom_analysis',
      description: 'Custom Document Analysis'
    },
    documents: [],
    persona: { role: '' },
    job_to_be_done: { task: '' }
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const response = await axios.get(`${API}/collections`);
      setCollections(response.data);
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    
    // Update documents in analysis request
    const documents = files.map(file => ({
      filename: file.name,
      title: file.name.replace('.pdf', '').replace(/_/g, ' ')
    }));
    
    setAnalysisRequest(prev => ({
      ...prev,
      documents: documents
    }));
  };

  const handlePersonaChange = (event) => {
    setAnalysisRequest(prev => ({
      ...prev,
      persona: { role: event.target.value }
    }));
  };

  const handleJobChange = (event) => {
    setAnalysisRequest(prev => ({
      ...prev,
      job_to_be_done: { task: event.target.value }
    }));
  };

  const handleSampleCollection = (collection) => {
    setAnalysisRequest(prev => ({
      ...prev,
      persona: { role: collection.persona },
      job_to_be_done: { task: collection.job_to_be_done }
    }));
  };

  const handleAnalyze = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one PDF file');
      return;
    }
    
    if (!analysisRequest.persona.role) {
      setError('Please enter a persona role');
      return;
    }
    
    if (!analysisRequest.job_to_be_done.task) {
      setError('Please enter a job to be done');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setAnalysisResult(null);

    try {
      const formData = new FormData();
      
      // Add files
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      // Add analysis request
      formData.append('analysis_request', JSON.stringify(analysisRequest));
      
      const response = await axios.post(`${API}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setAnalysisResult(response.data);
    } catch (error) {
      console.error('Analysis error:', error);
      setError(error.response?.data?.detail || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadJSON = () => {
    if (!analysisResult) return;
    
    const dataStr = JSON.stringify(analysisResult.result, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `analysis_${analysisResult.id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-600 p-2 rounded-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Persona-Driven Document Intelligence</h1>
              <p className="text-gray-600">Extract and prioritize relevant content based on user personas and tasks</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* File Upload */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">Upload Documents</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="flex flex-col items-center space-y-2">
                    <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <span className="text-lg text-gray-600">Click to upload PDF files</span>
                    <span className="text-sm text-gray-500">Support for multiple files (3-10 recommended)</span>
                  </div>
                </label>
              </div>
              
              {selectedFiles.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Selected Files ({selectedFiles.length})</h3>
                  <div className="space-y-2">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center space-x-2 text-sm">
                        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <span>{file.name}</span>
                        <span className="text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Analysis Configuration */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">Analysis Configuration</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Persona Role *
                  </label>
                  <input
                    type="text"
                    value={analysisRequest.persona.role}
                    onChange={handlePersonaChange}
                    placeholder="e.g., Travel Planner, HR Professional, Food Contractor"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job to be Done *
                  </label>
                  <textarea
                    value={analysisRequest.job_to_be_done.task}
                    onChange={handleJobChange}
                    placeholder="e.g., Plan a trip of 4 days for a group of 10 college friends"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Analysis Button */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || selectedFiles.length === 0}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  isAnalyzing || selectedFiles.length === 0
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isAnalyzing ? (
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>Analyzing Documents...</span>
                  </div>
                ) : (
                  'Analyze Documents'
                )}
              </button>
              
              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Sample Collections Sidebar */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">Sample Collections</h2>
              <div className="space-y-3">
                {collections.map((collection) => (
                  <div key={collection.id} className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                       onClick={() => handleSampleCollection(collection)}>
                    <h3 className="font-medium text-sm">{collection.name}</h3>
                    <p className="text-xs text-gray-600 mt-1">{collection.description}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-blue-600">{collection.document_count} documents</span>
                      <button className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        Use Template
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {analysisResult && (
          <div className="mt-8 bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Analysis Results</h2>
              <button
                onClick={downloadJSON}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Download JSON</span>
              </button>
            </div>
            
            <div className="p-6">
              {/* Metadata */}
              <div className="mb-6">
                <h3 className="font-medium mb-2">Analysis Metadata</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Persona:</span> {analysisResult.result.metadata.persona}
                    </div>
                    <div>
                      <span className="font-medium">Documents:</span> {analysisResult.result.metadata.input_documents.length}
                    </div>
                    <div className="col-span-2">
                      <span className="font-medium">Job to be Done:</span> {analysisResult.result.metadata.job_to_be_done}
                    </div>
                    <div>
                      <span className="font-medium">Processed:</span> {new Date(analysisResult.result.metadata.processing_timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>

              {/* Extracted Sections */}
              <div className="mb-6">
                <h3 className="font-medium mb-3">Extracted Sections ({analysisResult.result.extracted_sections.length})</h3>
                <div className="space-y-3">
                  {analysisResult.result.extracted_sections.map((section, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-sm">{section.section_title}</h4>
                        <div className="flex items-center space-x-2">
                          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                            Rank #{section.importance_rank}
                          </span>
                          <span className="text-xs text-gray-500">Page {section.page_number}</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{section.document}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Subsection Analysis */}
              <div>
                <h3 className="font-medium mb-3">Detailed Analysis ({analysisResult.result.subsection_analysis.length})</h3>
                <div className="space-y-4">
                  {analysisResult.result.subsection_analysis.map((subsection, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-sm">{subsection.document}</h4>
                        <span className="text-xs text-gray-500">Page {subsection.page_number}</span>
                      </div>
                      <p className="text-sm text-gray-700 leading-relaxed">{subsection.refined_text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
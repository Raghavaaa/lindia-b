"use client";

import { useEffect, useState } from 'react';

export default function DebugPage() {
  const [envVar, setEnvVar] = useState<string>('');
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');

  useEffect(() => {
    // Check environment variable
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    setEnvVar(backendUrl || 'NOT SET');

    // Test backend connection
    if (backendUrl) {
      fetch(`${backendUrl}/health`)
        .then(response => response.json())
        .then(data => {
          setBackendStatus(`✅ Connected: ${data.status} (v${data.version})`);
        })
        .catch(error => {
          setBackendStatus(`❌ Error: ${error.message}`);
        });
    } else {
      setBackendStatus('❌ No backend URL configured');
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">🔍 Debug Information</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Environment Variables</h2>
          <div className="space-y-2">
            <div className="flex items-center space-x-4">
              <span className="font-medium">NEXT_PUBLIC_BACKEND_URL:</span>
              <span className={`px-3 py-1 rounded ${
                envVar && envVar !== 'NOT SET' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {envVar}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Backend Connection</h2>
          <div className="space-y-2">
            <div className="flex items-center space-x-4">
              <span className="font-medium">Status:</span>
              <span className="px-3 py-1 rounded bg-blue-100 text-blue-800">
                {backendStatus}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Test</h2>
          <button
            onClick={() => {
              if (envVar && envVar !== 'NOT SET') {
                window.open(`${envVar}/health`, '_blank');
              } else {
                alert('Backend URL not configured');
              }
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Test Backend Health Check
          </button>
        </div>

        <div className="mt-8 text-sm text-gray-600">
          <p>This page helps debug the frontend-backend connection.</p>
          <p>If NEXT_PUBLIC_BACKEND_URL shows "NOT SET", the environment variable isn't configured properly.</p>
        </div>
      </div>
    </div>
  );
}

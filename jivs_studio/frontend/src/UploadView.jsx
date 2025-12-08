import { useState } from 'react';
import axios from 'axios';
import { Upload, Loader2, Sparkles } from 'lucide-react';

export default function UploadView({ onGenerate }) {
  const [files, setFiles] = useState([]);
  const [prompt, setPrompt] = useState("A modern SaaS dashboard with dark mode.");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('prompt', prompt);
    files.forEach(f => formData.append('files', f));

    try {
      const res = await axios.post('http://localhost:8000/generate', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onGenerate(res.data.image);
    } catch (err) {
      alert("Error generating image: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-10">
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Sparkles className="text-indigo-600" /> Start New Design
        </h2>

        {/* File Upload */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2 text-gray-600">Reference Images (Optional)</label>
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:bg-gray-50 transition cursor-pointer relative">
            <input 
              type="file" 
              multiple 
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
            <div className="flex flex-col items-center">
              <Upload className="h-10 w-10 text-gray-400 mb-2" />
              <p className="text-sm text-gray-500">Drag files here or click to upload</p>
              {files.length > 0 && (
                <div className="mt-4 flex gap-2 overflow-x-auto">
                  {files.map((f, i) => (
                    <span key={i} className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded">
                      {f.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Prompt Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2 text-gray-600">Design Brief</label>
          <textarea
            className="w-full p-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
            rows="4"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the UI you want to build..."
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition flex items-center justify-center gap-2"
        >
          {loading ? <><Loader2 className="animate-spin" /> Analyzing & Generating...</> : "Generate Concept"}
        </button>
      </div>
    </div>
  );
}
import { useState } from 'react';
import axios from 'axios';
import { Upload, Copy, Check, Code, FileCode, RefreshCw } from 'lucide-react';

export default function CodeGenerator() {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Settings
  const [framework, setFramework] = useState("HTML + Tailwind");
  const [prompt, setPrompt] = useState("");

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setImagePreview(URL.createObjectURL(selected));
    }
  };

  const handleGenerate = async () => {
    if (!file) return alert("Please upload an image first.");
    
    setLoading(true);
    setCode(""); // Clear previous code
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('framework', framework);
    formData.append('prompt', prompt);

    try {
      const res = await axios.post('http://localhost:8000/generate-raw-code', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCode(res.data.code);
    } catch (err) {
      console.error(err);
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 font-mono">
      
      {/* Header */}
      <header className="max-w-7xl mx-auto flex items-center justify-between mb-8 border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
                <FileCode size={24} />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">JiVS Code Generator</h1>
        </div>
        <div className="flex items-center gap-4">
            <select 
                value={framework} 
                onChange={(e) => setFramework(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            >
                <option>HTML + Tailwind</option>
                <option>React + Tailwind</option>
                <option>Bootstrap 5</option>
                <option>Vue.js</option>
            </select>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6 h-[80vh]">
        
        {/* LEFT COLUMN: INPUT */}
        <div className="flex flex-col gap-4">
            {/* Image Upload Area */}
            <div className="flex-1 bg-gray-800 rounded-xl border-2 border-dashed border-gray-700 relative overflow-hidden flex items-center justify-center group">
                {imagePreview ? (
                    <img src={imagePreview} alt="Upload" className="max-w-full max-h-full object-contain" />
                ) : (
                    <div className="text-center text-gray-500">
                        <Upload className="mx-auto h-12 w-12 mb-2 opacity-50" />
                        <p>Click or Drag Screenshot</p>
                    </div>
                )}
                <input 
                    type="file" 
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={handleFileChange}
                />
            </div>

            {/* Prompt Area */}
            <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Optional: Add specific requirements (e.g., 'Use a dark theme', 'Make buttons round')..."
                className="bg-gray-800 border border-gray-700 rounded-xl p-4 h-32 focus:ring-2 focus:ring-blue-500 outline-none resize-none text-sm text-gray-300"
            />

            <button 
                onClick={handleGenerate}
                disabled={loading || !file}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {loading ? <RefreshCw className="animate-spin" /> : <Code />} 
                Generate {framework}
            </button>
        </div>

        {/* RIGHT COLUMN: CODE OUTPUT */}
        <div className="flex flex-col bg-gray-800 rounded-xl border border-gray-700 overflow-hidden shadow-2xl">
            <div className="bg-gray-900 px-4 py-2 border-b border-gray-700 flex justify-between items-center">
                <span className="text-xs text-gray-400">generated_output.{framework.includes('React') ? 'jsx' : 'html'}</span>
                <button 
                    onClick={copyToClipboard}
                    disabled={!code}
                    className="flex items-center gap-2 text-xs font-semibold bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded-lg transition disabled:opacity-50"
                >
                    {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                    {copied ? "Copied!" : "Copy Code"}
                </button>
            </div>
            
            <div className="flex-1 relative overflow-hidden">
                {loading ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 animate-pulse">
                        <Code size={48} className="mb-4 text-blue-500" />
                        <p>Analyzing pixels...</p>
                        <p className="text-xs mt-2">Using Gemini 2.5 Flash Lite</p>
                    </div>
                ) : (
                    <textarea 
                        readOnly
                        value={code || "// Upload an image to generate code..."}
                        className="w-full h-full bg-[#0d1117] text-gray-300 p-4 font-mono text-sm outline-none resize-none"
                        spellCheck="false"
                    />
                )}
            </div>
        </div>

      </main>
    </div>
  );
}
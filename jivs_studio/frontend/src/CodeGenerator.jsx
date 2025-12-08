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
    setCode(""); 
    
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
    <div className="max-w-[1600px] mx-auto p-6 font-sans text-gray-800">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Code className="text-indigo-600" /> Code Snippet Generator
          </h2>
          <p className="text-sm text-gray-500 mt-1">Convert screenshots into raw, copy-pasteable code.</p>
        </div>

        <div className="flex items-center gap-4">
            <select 
                value={framework} 
                onChange={(e) => setFramework(e.target.value)}
                className="bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none shadow-sm"
            >
                <option>HTML + Tailwind</option>
                <option>React + Tailwind</option>
                <option>Bootstrap 5</option>
                <option>Vue.js</option>
            </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[75vh]">
        
        {/* LEFT COLUMN: INPUT */}
        <div className="flex flex-col gap-6 h-full">
            {/* Image Upload Area */}
            <div className="flex-1 bg-white rounded-2xl border-2 border-dashed border-gray-200 relative overflow-hidden flex items-center justify-center group hover:bg-gray-50 transition cursor-pointer">
                {imagePreview ? (
                    <img src={imagePreview} alt="Upload" className="max-w-full max-h-full object-contain p-4" />
                ) : (
                    <div className="text-center text-gray-400 group-hover:text-indigo-500 transition">
                        <Upload className="mx-auto h-12 w-12 mb-2 opacity-50" />
                        <p className="font-medium">Click or Drag Screenshot</p>
                    </div>
                )}
                <input 
                    type="file" 
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={handleFileChange}
                />
            </div>

            {/* Prompt Area */}
            <div className="bg-white p-1 rounded-xl shadow-sm border border-gray-200">
              <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Optional: Add specific requirements (e.g., 'Use a dark theme', 'Make buttons round')..."
                  className="w-full p-4 h-24 outline-none resize-none text-sm text-gray-700 bg-transparent"
              />
            </div>

            <button 
                onClick={handleGenerate}
                disabled={loading || !file}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-200"
            >
                {loading ? <RefreshCw className="animate-spin" /> : <FileCode />} 
                Generate {framework}
            </button>
        </div>

        {/* RIGHT COLUMN: CODE OUTPUT */}
        <div className="flex flex-col bg-[#1e1e1e] rounded-2xl overflow-hidden shadow-2xl border border-gray-800">
            {/* Editor Header */}
            <div className="bg-[#252526] px-4 py-3 border-b border-[#333] flex justify-between items-center">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <span className="text-xs text-gray-400 font-mono">
                  generated.{framework.toLowerCase().includes('react') ? 'jsx' : 'html'}
                </span>
                <button 
                    onClick={copyToClipboard}
                    disabled={!code}
                    className="flex items-center gap-2 text-xs font-semibold bg-[#333] hover:bg-[#444] text-white px-3 py-1.5 rounded-lg transition disabled:opacity-50"
                >
                    {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                    {copied ? "Copied" : "Copy"}
                </button>
            </div>
            
            <div className="flex-1 relative">
                {loading ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
                        <div className="animate-pulse flex flex-col items-center">
                          <Code size={48} className="mb-4 text-indigo-500" />
                          <p className="font-mono text-sm">Analyzing pixels...</p>
                        </div>
                    </div>
                ) : (
                    <textarea 
                        readOnly
                        value={code || "// Upload an image to generate code..."}
                        className="w-full h-full bg-[#1e1e1e] text-gray-300 p-6 font-mono text-sm outline-none resize-none"
                        spellCheck="false"
                    />
                )}
            </div>
        </div>

      </div>
    </div>
  );
}
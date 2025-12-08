import { useState, useRef } from 'react';
import axios from 'axios';
import * as htmlToImage from 'html-to-image';
import { Upload, Code, Download, RefreshCw, Smartphone, Monitor, ArrowLeft } from 'lucide-react';

export default function WebBuilder() {
  const [step, setStep] = useState(1); // 1=Upload, 2=Editor
  const [files, setFiles] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [htmlCode, setHtmlCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [device, setDevice] = useState("desktop"); // 'desktop' or 'mobile'
  
  const iframeRef = useRef(null);

  // --- API CALLS ---
  const handleGenerate = async () => {
    if (!prompt) return alert("Please enter a description");
    
    setLoading(true);
    const formData = new FormData();
    formData.append('prompt', prompt);
    files.forEach(f => formData.append('files', f));

    try {
      const res = await axios.post('http://localhost:8000/generate-code', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setHtmlCode(res.data.html);
      setStep(2);
      setPrompt(""); // Clear prompt for next step
    } catch (err) {
      console.error(err);
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!prompt) return alert("Please enter instructions to update");
    
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/refine-code', {
        current_html: htmlCode,
        instructions: prompt
      });
      setHtmlCode(res.data.html);
      setPrompt(""); // Clear prompt after success
    } catch (err) {
      console.error(err);
      alert("Refine Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // --- DOWNLOAD LOGIC ---
  const downloadImage = async () => {
    if (!iframeRef.current) return;
    
    try {
      // Access the iframe body
      const iframeBody = iframeRef.current.contentWindow.document.body;
      
      // We need to temporarily ensure the iframe content is fully visible/styled for capture
      const dataUrl = await htmlToImage.toPng(iframeBody, { 
        quality: 1.0, 
        pixelRatio: 2, // High resolution
        backgroundColor: '#ffffff'
      });
      
      const link = document.createElement('a');
      link.download = 'generated-website.png';
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('Download failed', error);
      alert("Could not generate image. Try using the '📸 Download Image' button inside the preview instead.");
    }
  };

  // --- RENDER HELPERS ---
  const fullSrcDoc = `
    <!DOCTYPE html>
    <html>
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
        <style>
            body { margin: 0; overflow-x: hidden; background: white; } 
            /* Ensure controls are clickable & pretty */
            #ui-controls button { transition: all 0.2s; }
            #ui-controls button:hover { transform: scale(1.05); }
        </style>
      </head>
      <body>
        ${htmlCode}
      </body>
    </html>
  `;

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 p-6 font-sans">
      
      {/* HEADER */}
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Code className="text-indigo-600" /> JiVS Web Builder
        </h1>
        {step === 2 && (
            <button onClick={() => setStep(1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-indigo-600 font-medium">
                <ArrowLeft size={16} /> Start Over
            </button>
        )}
      </header>

      {/* STEP 1: UPLOAD */}
      {step === 1 && (
        <div className="max-w-xl mx-auto mt-10 bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
          <h2 className="text-xl font-bold mb-4 text-gray-800">1. Upload Context</h2>
          
          <div className="border-2 border-dashed border-gray-200 rounded-xl p-10 mb-6 text-center hover:bg-gray-50 transition relative group cursor-pointer">
            <input 
              type="file" multiple className="absolute inset-0 opacity-0 cursor-pointer z-10"
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
            <div className="flex flex-col items-center">
                <div className="bg-indigo-50 p-3 rounded-full mb-3 group-hover:bg-indigo-100 transition">
                    <Upload className="h-6 w-6 text-indigo-600" />
                </div>
                <p className="font-medium text-gray-700">
                    {files.length > 0 ? `${files.length} files selected` : "Click to upload screenshots"}
                </p>
                <p className="text-xs text-gray-400 mt-1">Supports PNG, JPG</p>
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">2. Describe the Website</label>
            <textarea
                className="w-full p-4 bg-gray-50 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none transition"
                rows="4"
                placeholder="e.g. 'A modern SaaS landing page with a dark hero section, feature grid, and pricing table.'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
            />
          </div>
          
          <button 
            onClick={handleGenerate} 
            disabled={loading} 
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition flex justify-center items-center gap-2 shadow-lg shadow-indigo-200"
          >
            {loading ? <RefreshCw className="animate-spin" /> : "🚀 Generate Code"}
          </button>
        </div>
      )}

      {/* STEP 2: EDITOR & PREVIEW */}
      {step === 2 && (
        <div className="max-w-[1400px] mx-auto flex gap-6 h-[85vh]">
          
          {/* LEFT: PREVIEW PANE */}
          <div className="flex-1 bg-gray-200 rounded-2xl shadow-inner overflow-hidden flex flex-col relative border border-gray-300">
            {/* Device Toolbar */}
            <div className="bg-white p-3 flex justify-center gap-2 border-b">
                <button onClick={() => setDevice('desktop')} className={`p-2 rounded-lg transition ${device==='desktop' ? 'bg-indigo-100 text-indigo-600 shadow-sm' : 'text-gray-400 hover:bg-gray-100'}`}>
                    <Monitor size={20} />
                </button>
                <button onClick={() => setDevice('mobile')} className={`p-2 rounded-lg transition ${device==='mobile' ? 'bg-indigo-100 text-indigo-600 shadow-sm' : 'text-gray-400 hover:bg-gray-100'}`}>
                    <Smartphone size={20} />
                </button>
            </div>

            {/* Iframe Container */}
            <div className="flex-1 overflow-auto flex justify-center bg-gray-100/50 p-8">
                <iframe
                    ref={iframeRef}
                    srcDoc={fullSrcDoc}
                    title="Preview"
                    className={`bg-white shadow-2xl transition-all duration-500 ease-in-out border border-gray-200 ${
                        device === 'mobile' ? 'w-[375px] h-[667px] rounded-[30px] border-8 border-gray-800' : 'w-full h-full rounded-lg'
                    }`}
                />
            </div>
          </div>

          {/* RIGHT: CONTROLS PANE */}
          <div className="w-80 bg-white rounded-2xl shadow-xl p-6 flex flex-col border border-gray-100">
            <h3 className="font-bold text-lg mb-1 text-gray-800">Refine Design</h3>
            <p className="text-xs text-gray-500 mb-4">Describe changes to update the code.</p>
            
            {/* --- REMOVED THE HTML PREVIEW DIV FROM HERE --- */}

            <textarea
              className="w-full p-4 bg-gray-50 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm mb-4 h-40 resize-none"
              placeholder="What needs fixing? (e.g. 'Make the main button larger' or 'Change the background to blue')"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />

            <button 
                onClick={handleRefine} 
                disabled={loading} 
                className="w-full bg-gray-900 hover:bg-black text-white font-bold py-3 rounded-xl mb-4 transition flex justify-center gap-2 shadow-lg"
            >
                {loading ? <RefreshCw className="animate-spin w-5 h-5" /> : "✨ Update Code"}
            </button>

            <div className="border-t pt-6 mt-auto">
                <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                    <p className="text-xs text-blue-800 font-semibold mb-2">💡 Pro Tip:</p>
                    <p className="text-xs text-blue-600 mb-3">
                        Use the <b>Design Mode</b> button inside the preview (top right) to drag & drop elements or edit text manually.
                    </p>
                    
                    <button 
                        onClick={downloadImage} 
                        className="w-full py-2 bg-white border border-blue-200 text-blue-700 font-bold rounded-lg hover:bg-blue-50 text-xs flex justify-center items-center gap-2"
                    >
                        <Download size={14} /> Download PNG
                    </button>
                </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
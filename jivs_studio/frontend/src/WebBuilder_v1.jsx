import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import * as htmlToImage from 'html-to-image';
import { Upload, Code, Download, RefreshCw, Smartphone, Monitor } from 'lucide-react';

export default function WebBuilder() {
  const [step, setStep] = useState(1); // 1=Upload, 2=Editor
  const [files, setFiles] = useState([]);
  const [prompt, setPrompt] = useState("A landing page with a hero section and features.");
  const [htmlCode, setHtmlCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [device, setDevice] = useState("desktop"); // 'desktop' or 'mobile'
  
  const iframeRef = useRef(null);

  // --- API CALLS ---
  const handleGenerate = async () => {
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
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefine = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/refine-code', {
        current_html: htmlCode,
        instructions: prompt
      });
      setHtmlCode(res.data.html);
      setPrompt(""); // Clear prompt after success
    } catch (err) {
      alert("Refine Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- DOWNLOAD LOGIC ---
  const downloadImage = async () => {
    if (!iframeRef.current) return;
    
    try {
      // We capture the body inside the iframe
      const iframeBody = iframeRef.current.contentWindow.document.body;
      const dataUrl = await htmlToImage.toPng(iframeBody, { quality: 0.95 });
      
      const link = document.createElement('a');
      link.download = 'generated-website.png';
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('Download failed', error);
      alert("Could not generate image. Try waiting for images to load inside the preview.");
    }
  };

  // --- RENDER HELPERS ---
  // We wrap the generated HTML in a full document structure with Tailwind CDN
  //const fullSrcDoc = `
  //  <!DOCTYPE html>
  //  <html>
  //    <head>
  //      <script src="https://cdn.tailwindcss.com"></script>
  //      <style>body { margin: 0; overflow-x: hidden; }</style>
  //    </head>
  //    <body>
  //      ${htmlCode}
  //    </body>
  //  </html>
  //`;
  // inside WebBuilder.jsx

const fullSrcDoc = `
    <!DOCTYPE html>
    <html>
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
        <style>
            body { margin: 0; overflow-x: hidden; } 
            /* Ensure controls are clickable */
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
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Code className="text-indigo-600" /> JiVS Web Builder
        </h1>
        {step === 2 && (
            <button onClick={() => setStep(1)} className="text-sm text-gray-500 hover:text-indigo-600">
                Start Over
            </button>
        )}
      </header>

      {/* STEP 1: UPLOAD */}
      {step === 1 && (
        <div className="max-w-xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Upload Screenshot</h2>
          <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 mb-6 text-center hover:bg-gray-50 transition relative">
            <input 
              type="file" multiple className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
            <Upload className="mx-auto h-10 w-10 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500">
                {files.length > 0 ? `${files.length} files selected` : "Drag images here"}
            </p>
          </div>
          
          <textarea
            className="w-full p-4 bg-gray-50 rounded-xl mb-4 border border-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none"
            placeholder="Describe the website... (e.g. 'Modern portfolio with dark mode')"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          
          <button onClick={handleGenerate} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition flex justify-center items-center gap-2">
            {loading ? <RefreshCw className="animate-spin" /> : "Generate Website"}
          </button>
        </div>
      )}

      {/* STEP 2: EDITOR & PREVIEW */}
      {step === 2 && (
        <div className="max-w-7xl mx-auto flex gap-6 h-[80vh]">
          
          {/* PREVIEW PANE */}
          <div className="flex-1 bg-gray-200 rounded-xl shadow-inner overflow-hidden flex flex-col relative border border-gray-300">
            {/* Device Toolbar */}
            <div className="bg-white p-2 flex justify-center gap-4 border-b">
                <button onClick={() => setDevice('desktop')} className={`p-2 rounded ${device==='desktop' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-500'}`}>
                    <Monitor size={20} />
                </button>
                <button onClick={() => setDevice('mobile')} className={`p-2 rounded ${device==='mobile' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-500'}`}>
                    <Smartphone size={20} />
                </button>
            </div>

            {/* Iframe Container */}
            <div className="flex-1 overflow-auto flex justify-center bg-gray-100 p-4">
                <iframe
                    ref={iframeRef}
                    srcDoc={fullSrcDoc}
                    title="Preview"
                    className={`bg-white shadow-2xl transition-all duration-300 ${
                        device === 'mobile' ? 'w-[375px] h-[667px]' : 'w-full h-full'
                    }`}
                />
            </div>
          </div>

          {/* CONTROLS PANE */}
          <div className="w-96 bg-white rounded-xl shadow-xl p-6 flex flex-col border border-gray-100">
            <h3 className="font-bold text-lg mb-4">Refine Design</h3>
            
            <div className="flex-1 overflow-y-auto mb-4 bg-gray-50 p-4 rounded-lg border text-xs font-mono text-gray-600">
                {/* Simple Code View (Read Only) */}
                {htmlCode.slice(0, 500)}...
            </div>

            <textarea
              className="w-full p-3 bg-gray-50 rounded-lg border border-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm mb-4"
              rows="3"
              placeholder="What should we change? (e.g. 'Make the buttons larger')"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />

            <button onClick={handleRefine} disabled={loading} className="w-full bg-gray-900 hover:bg-black text-white font-bold py-3 rounded-lg mb-4 transition flex justify-center gap-2">
                {loading ? <RefreshCw className="animate-spin" /> : "Update Code"}
            </button>

            <div className="border-t pt-4 mt-auto">
                <button onClick={downloadImage} className="w-full py-3 border-2 border-indigo-600 text-indigo-700 font-bold rounded-lg hover:bg-indigo-50 flex justify-center items-center gap-2">
                    <Download size={18} /> Download Image
                </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
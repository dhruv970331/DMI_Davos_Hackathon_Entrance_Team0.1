import { useState } from 'react';
import axios from 'axios';
import { 
  Upload, Folder, FileCode, Play, Terminal, 
  CheckCircle, XCircle, RefreshCw, Box 
} from 'lucide-react';

export default function ProjectGenerator() {
  // Input State
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [framework, setFramework] = useState("React");
  
  // Output State
  const [generatedFiles, setGeneratedFiles] = useState(null); 
  const [selectedFileName, setSelectedFileName] = useState(null);
  
  // Test State
  const [testReport, setTestReport] = useState(null);
  
  // Loading States
  const [generating, setGenerating] = useState(false);
  const [testing, setTesting] = useState(false);

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const handleGenerate = async () => {
    if (!prompt) return alert("Please describe the project");
    setGenerating(true);
    setGeneratedFiles(null);
    setTestReport(null);

    try {
      let imageBase64 = null;
      if (file) imageBase64 = await convertToBase64(file);

      const res = await axios.post('http://localhost:8000/generate-project', {
        framework, description: prompt, image_data: imageBase64
      });
      
      setGeneratedFiles(res.data.files);
      setSelectedFileName(Object.keys(res.data.files)[0]);
    } catch (err) {
      console.error(err);
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleRunTests = async () => {
    if (!generatedFiles) return;
    setTesting(true);
    setTestReport(null);

    try {
      const res = await axios.post('http://localhost:8000/run-tests', {
        code_files: generatedFiles, framework
      });
      setTestReport(res.data);
    } catch (err) {
      console.error(err);
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] font-sans bg-white">
      
      {/* 1. TOP BAR */}
      <div className="bg-white border-b border-gray-200 p-4 shadow-sm z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
           
           <div className="flex items-center gap-4 flex-1">
              {/* File Input */}
              <div className="relative group">
                  <input type="file" onChange={(e) => setFile(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer" />
                  <button className="flex items-center gap-2 bg-gray-50 hover:bg-gray-100 text-gray-700 px-4 py-2 rounded-lg border border-gray-200 text-sm transition font-medium">
                    <Upload size={16} /> {file ? file.name : "Upload Mockup"}
                  </button>
              </div>

              {/* Framework Select */}
              <select 
                value={framework} 
                onChange={(e) => setFramework(e.target.value)}
                className="bg-gray-50 border border-gray-200 text-gray-700 text-sm rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="React">React + Vite</option>
                <option value="Vue">Vue 3</option>
                <option value="Angular">Angular</option>
              </select>

              {/* Prompt Input */}
              <input 
                type="text" 
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe app logic (e.g. 'Login page with JWT auth')..."
                className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
              />
           </div>

           <button 
             onClick={handleGenerate} 
             disabled={generating}
             className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition shadow-md shadow-indigo-100"
           >
             {generating ? <RefreshCw className="animate-spin" size={16}/> : <Box size={16} />}
             Build Project
           </button>
        </div>
      </div>

      {/* 2. MAIN WORKSPACE */}
      <div className="flex-1 flex overflow-hidden">
        
        {!generatedFiles ? (
           <div className="flex-1 flex flex-col items-center justify-center text-gray-400 bg-gray-50">
              <Folder size={80} className="mb-4 text-gray-300" />
              <p className="text-lg font-medium text-gray-500">Ready to architect your project</p>
           </div>
        ) : (
           <>
             {/* LEFT: FILE EXPLORER (Light) */}
             <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
                <div className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <Folder size={14}/> Explorer
                </div>
                <div className="flex-1 overflow-y-auto px-2">
                   {Object.keys(generatedFiles).map((fileName) => (
                      <button
                        key={fileName}
                        onClick={() => setSelectedFileName(fileName)}
                        className={`w-full text-left px-3 py-2 text-sm flex items-center gap-2 rounded-md transition mb-1 ${
                          selectedFileName === fileName 
                            ? 'bg-white text-indigo-600 shadow-sm border border-gray-100 font-medium' 
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                      >
                        <FileCode size={14} className={selectedFileName === fileName ? "text-indigo-500" : "text-gray-400"} />
                        {fileName}
                      </button>
                   ))}
                </div>
                
                <div className="p-4 border-t border-gray-200 bg-white">
                   <button 
                     onClick={handleRunTests} 
                     disabled={testing}
                     className="w-full bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition"
                   >
                      {testing ? <RefreshCw className="animate-spin" size={12} /> : <Play size={12} />}
                      Run System Tests
                   </button>
                </div>
             </div>

             {/* CENTER: CODE EDITOR (Dark for contrast) */}
             <div className="flex-1 flex flex-col bg-[#1e1e1e]">
                {/* File Tab */}
                <div className="bg-[#252526] border-b border-[#333] px-4 py-2 text-sm text-gray-300 flex items-center gap-2 font-mono">
                   <FileCode size={14} className="text-blue-400" />
                   {selectedFileName}
                </div>
                
                <textarea 
                   readOnly
                   value={generatedFiles[selectedFileName] || ""}
                   className="flex-1 w-full bg-[#1e1e1e] p-6 font-mono text-sm text-gray-300 outline-none resize-none leading-relaxed"
                   spellCheck="false"
                />

                {/* BOTTOM: TERMINAL (Dark) */}
                {testReport && (
                  <div className="h-64 bg-[#1e1e1e] border-t border-[#333] flex flex-col shadow-2xl">
                     <div className="px-4 py-2 bg-[#252526] text-xs font-bold text-gray-400 flex justify-between items-center border-b border-[#333]">
                        <span className="flex items-center gap-2"><Terminal size={12}/> CONSOLE / TESTS</span>
                        <span className={testReport.summary.failed > 0 ? "text-red-400" : "text-green-400"}>
                           {testReport.summary.passed} Passed, {testReport.summary.failed} Failed
                        </span>
                     </div>
                     <div className="flex-1 overflow-y-auto p-4 font-mono text-xs">
                        {testReport.tests.map((test, idx) => (
                           <div key={idx} className="mb-2 border-b border-[#333] pb-2 last:border-0">
                              <div className="flex items-center gap-2 mb-1">
                                 {test.outcome === 'passed' 
                                   ? <CheckCircle size={14} className="text-green-500"/> 
                                   : <XCircle size={14} className="text-red-500"/>
                                 }
                                 <span className={test.outcome === 'passed' ? "text-gray-400" : "text-red-400 font-bold"}>
                                    {test.name}
                                 </span>
                                 <span className="text-gray-600 ml-auto">{test.duration.toFixed(4)}s</span>
                              </div>
                              {test.message && (
                                 <pre className="text-red-300 pl-6 whitespace-pre-wrap opacity-80">{test.message}</pre>
                              )}
                           </div>
                        ))}
                     </div>
                  </div>
                )}
             </div>
           </>
        )}
      </div>
    </div>
  );
}
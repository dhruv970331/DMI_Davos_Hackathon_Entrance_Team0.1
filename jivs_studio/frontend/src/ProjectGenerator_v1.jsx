import { useState } from 'react';
import axios from 'axios';
import { 
  Upload, Folder, FileCode, Play, Terminal, 
  CheckCircle, XCircle, AlertCircle, RefreshCw, Box 
} from 'lucide-react';

export default function ProjectGenerator() {
  // Input State
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [framework, setFramework] = useState("React");
  
  // Output State
  const [generatedFiles, setGeneratedFiles] = useState(null); // { "App.jsx": "code..." }
  const [selectedFileName, setSelectedFileName] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  
  // Test State
  const [testReport, setTestReport] = useState(null);
  
  // Loading States
  const [generating, setGenerating] = useState(false);
  const [testing, setTesting] = useState(false);

  // --- HELPER: CONVERT IMAGE TO BASE64 ---
  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  // --- API: GENERATE PROJECT ---
  const handleGenerate = async () => {
    if (!prompt) return alert("Please describe the project");
    
    setGenerating(true);
    setGeneratedFiles(null);
    setTestReport(null);

    try {
      let imageBase64 = null;
      if (file) {
        imageBase64 = await convertToBase64(file);
      }

      const payload = {
        framework: framework,
        description: prompt,
        image_data: imageBase64
      };

      const res = await axios.post('http://localhost:8000/generate-project', payload);
      
      setGeneratedFiles(res.data.files);
      setAnalysis(res.data.analysis);
      
      // Select the first file automatically
      const firstFile = Object.keys(res.data.files)[0];
      setSelectedFileName(firstFile);

    } catch (err) {
      console.error(err);
      alert("Generation Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  // --- API: RUN TESTS ---
  const handleRunTests = async () => {
    if (!generatedFiles) return;
    
    setTesting(true);
    setTestReport(null);

    try {
      const payload = {
        code_files: generatedFiles,
        framework: framework
      };

      const res = await axios.post('http://localhost:8000/run-tests', payload);
      setTestReport(res.data);
    } catch (err) {
      console.error(err);
      alert("Test Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-300 font-sans flex flex-col">
      
      {/* 1. TOP BAR: CONFIGURATION */}
      <div className="bg-[#161b22] border-b border-gray-800 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4 w-full max-w-4xl">
           {/* File Input */}
           <div className="relative group">
              <input 
                type="file" 
                onChange={(e) => setFile(e.target.files[0])}
                className="absolute inset-0 opacity-0 cursor-pointer w-full" 
              />
              <button className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-md border border-gray-700 text-sm transition">
                <Upload size={16} /> {file ? file.name : "Upload Image"}
              </button>
           </div>

           {/* Framework Select */}
           <select 
             value={framework} 
             onChange={(e) => setFramework(e.target.value)}
             className="bg-gray-800 border border-gray-700 text-sm rounded-md px-3 py-2 outline-none focus:border-blue-500"
           >
             <option value="React">React + Vite</option>
             <option value="Vue">Vue 3</option>
             <option value="Angular">Angular</option>
             <option value="Python">Python (Streamlit)</option>
           </select>

           {/* Prompt Input */}
           <input 
             type="text" 
             value={prompt}
             onChange={(e) => setPrompt(e.target.value)}
             placeholder="Describe app (e.g. 'Login page with validation')..."
             className="flex-1 bg-[#0d1117] border border-gray-700 rounded-md px-3 py-2 text-sm outline-none focus:border-blue-500"
           />

           {/* Generate Button */}
           <button 
             onClick={handleGenerate} 
             disabled={generating}
             className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-md text-sm font-bold flex items-center gap-2 transition disabled:opacity-50"
           >
             {generating ? <RefreshCw className="animate-spin" size={16}/> : <Box size={16} />}
             Build Project
           </button>
        </div>
      </div>

      {/* 2. MAIN WORKSPACE (Only shown after generation) */}
      <div className="flex-1 flex overflow-hidden">
        
        {!generatedFiles ? (
           // EMPTY STATE
           <div className="flex-1 flex flex-col items-center justify-center text-gray-600">
              <Folder size={64} className="mb-4 opacity-20" />
              <p>Ready to generate a multi-file project structure.</p>
           </div>
        ) : (
           <>
             {/* LEFT SIDEBAR: FILE EXPLORER */}
             <div className="w-64 bg-[#161b22] border-r border-gray-800 flex flex-col">
                <div className="p-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Explorer</div>
                <div className="flex-1 overflow-y-auto">
                   {Object.keys(generatedFiles).map((fileName) => (
                      <button
                        key={fileName}
                        onClick={() => setSelectedFileName(fileName)}
                        className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-gray-800 transition ${selectedFileName === fileName ? 'bg-blue-900/30 text-blue-400 border-l-2 border-blue-500' : 'text-gray-400'}`}
                      >
                        <FileCode size={14} />
                        {fileName}
                      </button>
                   ))}
                </div>
                
                {/* TEST RUNNER BUTTON */}
                <div className="p-4 border-t border-gray-800">
                   <button 
                     onClick={handleRunTests} 
                     disabled={testing}
                     className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md text-xs font-bold flex items-center justify-center gap-2 transition"
                   >
                      {testing ? <RefreshCw className="animate-spin" size={12} /> : <Play size={12} />}
                      Run System Tests
                   </button>
                </div>
             </div>

             {/* CENTER: CODE EDITOR */}
             <div className="flex-1 flex flex-col bg-[#0d1117]">
                {/* File Tab */}
                <div className="bg-[#0d1117] border-b border-gray-800 px-4 py-2 text-sm text-gray-400 flex items-center gap-2">
                   <FileCode size={14} className="text-blue-500" />
                   {selectedFileName}
                </div>
                
                {/* Code Content */}
                <textarea 
                   readOnly
                   value={generatedFiles[selectedFileName] || ""}
                   className="flex-1 w-full bg-[#0d1117] p-4 font-mono text-sm text-gray-300 outline-none resize-none"
                   spellCheck="false"
                />

                {/* BOTTOM PANEL: TERMINAL / TEST RESULTS */}
                {testReport && (
                  <div className="h-64 bg-[#161b22] border-t border-gray-800 flex flex-col">
                     <div className="px-4 py-2 bg-[#21262d] text-xs font-bold text-gray-400 flex justify-between items-center">
                        <span className="flex items-center gap-2"><Terminal size={12}/> TEST RESULTS</span>
                        <span className={testReport.summary.failed > 0 ? "text-red-400" : "text-green-400"}>
                           {testReport.summary.passed} Passed, {testReport.summary.failed} Failed
                        </span>
                     </div>
                     <div className="flex-1 overflow-y-auto p-4 font-mono text-xs">
                        {testReport.tests.map((test, idx) => (
                           <div key={idx} className="mb-2 border-b border-gray-800 pb-2 last:border-0">
                              <div className="flex items-center gap-2 mb-1">
                                 {test.outcome === 'passed' 
                                   ? <CheckCircle size={14} className="text-green-500"/> 
                                   : <XCircle size={14} className="text-red-500"/>
                                 }
                                 <span className={test.outcome === 'passed' ? "text-gray-300" : "text-red-300 font-bold"}>
                                    {test.name}
                                 </span>
                                 <span className="text-gray-600 ml-auto">{test.duration.toFixed(4)}s</span>
                              </div>
                              {test.message && (
                                 <pre className="text-red-400 pl-6 whitespace-pre-wrap">{test.message}</pre>
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
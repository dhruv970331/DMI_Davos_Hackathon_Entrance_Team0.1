import { useState } from 'react';
import { Image, Layers, FileCode, Box } from 'lucide-react'; // Icons

// Import Views
import UploadView from './UploadView';
import EditorView from './EditorView';
import WebBuilder from './WebBuilder'; // Ensure this matches your filename (e.g. WebBuilder.jsx)
import CodeGenerator from './CodeGenerator'; 
import ProjectGenerator from './ProjectGenerator'; 

function App() {
  // Modes: 'image', 'web', 'code', 'project'
  // Defaulting to 'project' as it's the newest feature, change as desired.
  const [mode, setMode] = useState('project'); 
  
  // State for the Image Gen mode
  const [generatedImage, setGeneratedImage] = useState(null);

  // Helper for tab styling
  const buttonClass = (targetMode) => `
    flex items-center gap-2 px-4 py-2 rounded-md text-sm font-semibold transition-all duration-200
    ${mode === targetMode 
      ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-black/5' 
      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50'
    }
  `;

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      
      {/* --- GLOBAL HEADER --- */}
      <header className="bg-white border-b px-6 py-3 shadow-sm flex items-center justify-between sticky top-0 z-50">
        
        {/* Logo Area */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-indigo-200 shadow-lg">
            J
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 leading-tight">JiVS Studio</h1>
            <p className="text-xs text-gray-500 font-medium">AI Interface Architect</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-gray-100 p-1 rounded-lg flex border border-gray-200 overflow-x-auto">
           {/* 1. Image Gen (DALL-E) */}
           <button onClick={() => setMode('image')} className={buttonClass('image')}>
             <Image size={16} /> Image
           </button>
           
           {/* 2. Web Builder (HTML Preview + Design Mode) */}
           <button onClick={() => setMode('web')} className={buttonClass('web')}>
             <Layers size={16} /> Web Builder
           </button>

           {/* 3. Code Generator (Raw Snippets) */}
           <button onClick={() => setMode('code')} className={buttonClass('code')}>
             <FileCode size={16} /> Snippet
           </button>

           {/* 4. Project Generator (Multi-file + Tests) */}
           <button onClick={() => setMode('project')} className={buttonClass('project')}>
             <Box size={16} /> Project
           </button>
        </div>
      </header>
      
      {/* --- MAIN CONTENT --- */}
      <main>
        {/* Render components based on selected mode */}
        
        {mode === 'project' && <ProjectGenerator />}
        
        {mode === 'code' && <CodeGenerator />}
        
        {mode === 'web' && <WebBuilder />}
        
        {mode === 'image' && (
           /* Image Gen has its own sub-state for upload vs editor */
           <div className="max-w-7xl mx-auto p-6">
             {!generatedImage ? (
               <UploadView onGenerate={setGeneratedImage} />
             ) : (
               <EditorView 
                 initialImage={generatedImage} 
                 onReset={() => setGeneratedImage(null)} 
               />
             )}
           </div>
        )}
      </main>

    </div>
  );
}

export default App;
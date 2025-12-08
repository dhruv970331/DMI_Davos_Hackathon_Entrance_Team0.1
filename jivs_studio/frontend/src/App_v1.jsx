import { useState } from 'react';
import { Image, Code, Layers } from 'lucide-react'; // Icons for the toggle

// Import your views
import UploadView from './UploadView';
import EditorView from './EditorView';
import WebBuilder from './WebBuilder'; // <--- Import the new component

function App() {
  // State to toggle between modes: 'web' (New) or 'image' (Old)
  const [mode, setMode] = useState('web'); 
  
  // State for the old Image Gen mode
  const [generatedImage, setGeneratedImage] = useState(null);

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

        {/* Mode Toggle Switch */}
        <div className="bg-gray-100 p-1 rounded-lg flex border border-gray-200">
           <button 
             onClick={() => setMode('image')}
             className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-semibold transition-all duration-200 ${
               mode === 'image' 
                 ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-black/5' 
                 : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50'
             }`}
           >
             <Image size={16} /> Image Gen
           </button>
           <button 
             onClick={() => setMode('web')}
             className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-semibold transition-all duration-200 ${
               mode === 'web' 
                 ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-black/5' 
                 : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50'
             }`}
           >
             <Code size={16} /> Web Builder
           </button>
        </div>
      </header>
      
      {/* --- MAIN CONTENT --- */}
      <main>
        {mode === 'web' ? (
           /* NEW MODE: The HTML/Tailwind Web Builder */
           /* Note: WebBuilder has its own internal container logic */
           <WebBuilder />
        ) : (
           /* OLD MODE: The DALL-E Image Generator */
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
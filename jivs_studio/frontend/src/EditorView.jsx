import { useState, useRef, useEffect } from 'react';
import { Stage, Layer, Image as KonvaImage, Rect, Transformer } from 'react-konva';
import axios from 'axios';
import { Download, RefreshCw, Undo, Save } from 'lucide-react';

const Rectangle = ({ shapeProps, isSelected, onSelect, onChange }) => {
  const shapeRef = useRef();
  const trRef = useRef();

  useEffect(() => {
    if (isSelected && trRef.current) {
      trRef.current.nodes([shapeRef.current]);
      trRef.current.getLayer().batchDraw();
    }
  }, [isSelected]);

  return (
    <>
      <Rect
        onClick={onSelect}
        onTap={onSelect}
        ref={shapeRef}
        {...shapeProps}
        draggable
        onDragEnd={(e) => {
          onChange({ ...shapeProps, x: e.target.x(), y: e.target.y() });
        }}
        onTransformEnd={() => {
          const node = shapeRef.current;
          const scaleX = node.scaleX();
          const scaleY = node.scaleY();
          node.scaleX(1);
          node.scaleY(1);
          onChange({
            ...shapeProps,
            x: node.x(),
            y: node.y(),
            width: Math.max(5, node.width() * scaleX),
            height: Math.max(node.height() * scaleY),
          });
        }}
        fill="rgba(255, 0, 0, 0.2)"
        stroke="red"
        strokeWidth={2}
      />
      {isSelected && <Transformer ref={trRef} rotateEnabled={false} />}
    </>
  );
};

export default function EditorView({ initialImage, onReset }) {
  const [image, setImage] = useState(initialImage);
  const [rectangles, setRectangles] = useState([]);
  const [selectedId, selectShape] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  
  // Canvas Refs
  const stageRef = useRef(null);
  const [imageObj, setImageObj] = useState(null);

  // Load Image Object for Konva
  useEffect(() => {
    const img = new window.Image();
    img.src = image;
    img.onload = () => setImageObj(img);
  }, [image]);

  const addRectangle = () => {
    const newRect = {
      x: 100, y: 100, width: 150, height: 100,
      id: `rect${rectangles.length + 1}`,
    };
    setRectangles([...rectangles, newRect]);
  };

  const handleRefine = async () => {
    setLoading(true);
    selectShape(null); // Deselect before capturing

    // 1. Capture the current stage (Image + Red Boxes)
    // We export to dataURL
    const annotationOverlay = stageRef.current.toDataURL({ pixelRatio: 2 });

    try {
      const res = await axios.post('http://localhost:8000/refine', {
        original_image: image,
        annotation_overlay: annotationOverlay,
        instructions: prompt
      });
      
      // Update with new image
      setImage(res.data.image);
      setRectangles([]); // Clear boxes after update
      setPrompt("");
    } catch (err) {
      alert("Refinement failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.download = 'jivs-design.png';
    link.href = image;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex gap-6 h-[85vh]">
      {/* LEFT: Canvas */}
      <div className="flex-1 bg-gray-200 rounded-xl overflow-hidden flex items-center justify-center relative border border-gray-300 shadow-inner">
        {imageObj ? (
          <Stage
            width={800} // Fixed workspace size
            height={600}
            ref={stageRef}
            onMouseDown={(e) => {
              const clickedOnEmpty = e.target === e.target.getStage();
              if (clickedOnEmpty) selectShape(null);
            }}
          >
            <Layer>
              {/* Background Image */}
              <KonvaImage image={imageObj} width={800} height={600} fit="contain" />
              {/* Annotations */}
              {rectangles.map((rect, i) => (
                <Rectangle
                  key={i}
                  shapeProps={rect}
                  isSelected={rect.id === selectedId}
                  onSelect={() => selectShape(rect.id)}
                  onChange={(newAttrs) => {
                    const rects = rectangles.slice();
                    rects[i] = newAttrs;
                    setRectangles(rects);
                  }}
                />
              ))}
            </Layer>
          </Stage>
        ) : (
          <div className="text-gray-500">Loading Canvas...</div>
        )}
        
        {/* Floating Toolbar */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white px-4 py-2 rounded-full shadow-lg flex gap-4">
          <button onClick={addRectangle} className="text-sm font-semibold text-red-600 hover:bg-red-50 px-3 py-1 rounded-full transition">
            + Add Annotation Box
          </button>
          <button onClick={() => setRectangles([])} className="text-sm text-gray-500 hover:text-gray-800">
            Clear Boxes
          </button>
        </div>
      </div>

      {/* RIGHT: Controls */}
      <div className="w-80 bg-white rounded-xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100">
        <h3 className="font-bold text-lg text-gray-800">Refine Design</h3>
        <p className="text-sm text-gray-500">
          Draw red boxes on the canvas to highlight areas, then describe the change below.
        </p>

        <textarea
          className="w-full p-3 bg-gray-50 rounded-lg border border-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
          rows="4"
          placeholder="e.g. 'Move the button inside the red box' or 'Make this section blue'"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />

        <button
          onClick={handleRefine}
          disabled={loading || rectangles.length === 0}
          className={`w-full py-3 rounded-lg font-bold text-white flex items-center justify-center gap-2 transition ${
            loading || rectangles.length === 0 ? 'bg-gray-400' : 'bg-indigo-600 hover:bg-indigo-700'
          }`}
        >
          {loading ? <RefreshCw className="animate-spin w-4 h-4" /> : <RefreshCw className="w-4 h-4" />}
          Update Design
        </button>

        <div className="border-t pt-4 mt-auto flex flex-col gap-2">
          <button 
            onClick={handleDownload}
            className="w-full py-2 border-2 border-indigo-600 text-indigo-700 font-semibold rounded-lg hover:bg-indigo-50 flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" /> Download Final
          </button>
          
          <button 
            onClick={onReset}
            className="w-full py-2 text-gray-500 hover:text-gray-800 text-sm flex items-center justify-center gap-2"
          >
            <Undo className="w-4 h-4" /> Start Over
          </button>
        </div>
      </div>
    </div>
  );
}
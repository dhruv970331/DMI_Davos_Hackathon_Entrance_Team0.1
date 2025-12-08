<div align="center">

# Alchemy Studio

![Alchemy Studio Logo](./AlchemyStudio_Logo.png)

**Alchemy Studio** is a powerful, AI-driven design automation tool that transforms design workflows by automatically converting designs into functional code and deployable projects. Built with modern web technologies, Alchemy Studio streamlines the entire design-to-development pipeline, enabling designers and developers to collaborate seamlessly.

</div>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Overview

Alchemy Studio addresses the critical gap in design automation by providing an intelligent platform that:

- **Uploads Design Assets**: Import design templates and mockups
- **Analyzes Visual Content**: Intelligently extracts design elements and structure
- **Generates Code**: Automatically produces clean, production-ready code
- **Builds Projects**: Creates complete, deployable project structures
- **Enables Collaboration**: Bridges the gap between designers and developers

The tool leverages advanced computer vision, vector embeddings, and large language models to understand design intent and translate it into functional implementations.

## Features

### 🎨 Core Capabilities

1. **Image Upload & Analysis**
   - Upload design mockups, wireframes, and templates
   - Intelligent visual parsing and element extraction
   - Support for multiple image formats

2. **Code Generation**
   - Automatic HTML/CSS/JavaScript generation from designs
   - Template-based code creation
   - Clean, readable, and maintainable output
   - Real-time code preview

3. **Web Builder**
   - Interactive visual editor for design components
   - Canvas-based design manipulation using Konva.js
   - Real-time preview capabilities
   - Drag-and-drop component editing

4. **Project Generator**
   - Creates complete, ready-to-deploy projects
   - Structured folder hierarchies
   - Includes configuration files and dependencies
   - Pre-configured build and development setups

5. **Vector Store Integration**
   - Semantic search over design components
   - Intelligent similarity matching
   - Template recommendation system

### 🤖 AI-Powered Features

- **Design Understanding**: Uses vector embeddings to comprehend design semantics
- **Intelligent Suggestions**: Provides smart recommendations based on design patterns
- **Automated Code Review**: Ensures code quality and best practices
- **Template Optimization**: Continuously improves generated templates

## Project Structure

```
Alchemy Studio/
├── frontend/                    # React-based user interface
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── UploadView.jsx       # Design upload interface
│   │   ├── EditorView.jsx       # Design editor component
│   │   ├── WebBuilder.jsx       # Interactive web builder
│   │   ├── CodeGenerator.jsx    # Code generation interface
│   │   ├── ProjectGenerator.jsx # Project creation tool
│   │   ├── App.css              # Global styles
│   │   └── assets/              # Images and static assets
│   ├── package.json             # Frontend dependencies
│   ├── vite.config.js           # Vite build configuration
│   └── index.html               # HTML entry point
│
├── backend/                     # Python FastAPI server
│   ├── main.py                  # Application entry point
│   ├── compare_images.py        # Image comparison utilities
│   ├── vector_store.py          # Vector database operations
│   ├── ingest_template.py       # Template ingestion pipeline
│   └── requirements.txt         # Python dependencies
│
└── jivs_studio/                 # Integrated project root
    ├── frontend/                # Frontend source
    └── backend/                 # Backend source
```

## Tech Stack

### Frontend
- **React 19.2**: Modern UI framework with hooks
- **Vite 5**: Fast build tool and dev server
- **Konva.js 10**: Canvas-based drawing and manipulation
- **TailwindCSS**: Utility-first CSS framework
- **React Konva 19**: React bindings for Konva
- **Axios**: HTTP client for API communication
- **html-to-image**: Convert DOM to images
- **jszip**: ZIP file creation for project exports
- **Lucide React**: Beautiful icon library

### Backend
- **Python 3.8+**: Core language
- **FastAPI**: Modern async web framework
- **Vector Store**: Semantic search and embeddings
- **Image Processing**: PIL/OpenCV for image analysis
- **Template Engine**: Dynamic code generation

## Getting Started

### Prerequisites

- **Node.js 16+** for frontend
- **Python 3.8+** for backend
- **npm or yarn** for package management

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The backend API will be available at `http://localhost:8000`

## Usage

### Workflow

1. **Upload Phase**
   - Navigate to the "Upload" tab
   - Upload your design mockup or template image
   - System analyzes and processes the design

2. **Editing Phase** (Optional)
   - Use the interactive web builder to refine designs
   - Adjust elements, colors, and layouts
   - Preview changes in real-time

3. **Code Generation**
   - Click "Generate Code" to create HTML/CSS/JS
   - Preview generated code
   - Download or copy to clipboard

4. **Project Generation**
   - Create a complete project structure
   - Configure project settings
   - Download as ZIP for immediate deployment

### API Endpoints

The backend provides RESTful APIs for:
- Design analysis and processing
- Template ingestion and management
- Vector store operations
- Code generation
- Project creation

## Architecture

### Design Philosophy

Alchemy Studio follows a modular, scalable architecture:

1. **Separation of Concerns**: Frontend (UI/UX) and backend (processing) are clearly separated
2. **Component-Based Frontend**: Reusable React components for different workflows
3. **API-Driven Backend**: Stateless FastAPI endpoints for scalability
4. **Vector-Powered Intelligence**: Semantic understanding through embeddings
5. **Template-Based Generation**: Efficient code generation through templates

### Data Flow

```
User Input (Design Image)
        ↓
[Frontend Upload Component]
        ↓
[Backend Image Analysis]
        ↓
[Vector Store Processing]
        ↓
[Template Matching & Generation]
        ↓
[Code Output / Project Export]
        ↓
User (Generated Code/Project)
```

## Key Components

### Frontend Components

- **UploadView**: Handles file uploads and initial processing
- **EditorView**: Displays and allows editing of extracted design elements
- **WebBuilder**: Canvas-based visual editor with Konva.js
- **CodeGenerator**: Displays and manages generated code
- **ProjectGenerator**: Creates and configures complete projects

### Backend Modules

- **vector_store.py**: Manages vector embeddings and semantic search
- **compare_images.py**: Analyzes and compares design images
- **ingest_template.py**: Processes and stores design templates
- **main.py**: FastAPI application with all endpoints

## Development

### Adding New Features

1. Create React components in `frontend/src/`
2. Add corresponding backend endpoints in `backend/main.py`
3. Update the vector store if using semantic features
4. Test thoroughly across both frontend and backend

### Code Quality

- Run `npm run lint` in frontend for ESLint checks
- Follow PEP 8 for Python code
- Add docstrings to Python functions
- Use meaningful commit messages

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Performance Optimization

- **Frontend**: Leverages Vite for fast builds and hot module replacement
- **Backend**: Uses async FastAPI for handling concurrent requests
- **Vector Store**: Optimized embeddings for quick similarity matching
- **Image Processing**: Efficient algorithms for design analysis

## Troubleshooting

### Common Issues

**Frontend won't start**
- Ensure Node.js version is 16+
- Delete `node_modules` and `package-lock.json`, then reinstall
- Check port 5173 is available

**Backend connection issues**
- Verify backend is running on `localhost:8000`
- Check firewall settings
- Ensure Python dependencies are installed

**Image upload fails**
- Verify image format is supported (PNG, JPG, SVG)
- Check image file size
- Ensure backend is processing correctly

## Future Roadmap

- [ ] Multi-page design support
- [ ] Real-time collaboration
- [ ] Advanced CSS frameworks (Tailwind, Bootstrap)
- [ ] React component generation
- [ ] Mobile app support
- [ ] Design system export
- [ ] Version control integration

## License

This project is part of the DMI Davos Hackathon. For licensing details, please refer to the project guidelines.

## Contact & Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the hackathon challenge documentation

---

**Built with ❤️ for the DMI Davos Hackathon**

**Version**: 0.1.0  
**Last Updated**: December 2025

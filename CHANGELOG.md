# Changelog

All notable changes to the **AlchemyStudio** project will be documented in this file.

The project has undergone a major architectural shift, moving from a monolithic Streamlit prototype to a decoupled React frontend and FastAPI backend.

## [Unreleased] - 2025-12-08

### 🚀 Major Architectural Changes

* **Deprecated Streamlit Prototype:** The initial Streamlit application (`streamlit_app/`) has been deprecated and serves only as a conceptual reference.
* **New React Frontend:** Introduced a modern, component-based frontend built with React (`frontend/`). This provides a more dynamic and responsive user experience for the creative studio.
* **New FastAPI Backend:** Established a robust backend API using FastAPI (`backend/`). This server now handles all core logic, including AI interactions, file processing, and code generation.

### ✨ New Features

#### Frontend (React)
* **Marketing & PR Persona Flow:** A dedicated workflow for generating marketing assets like banners and posters.
* **Full UI/UX Persona Flow:** A separate workflow for generating complete, functional Vue.js applications.
* **Design Studio Interface:** A drag-and-drop interface for uploading reference images and brand assets.
* **Live Preview:** Real-time preview of generated HTML/CSS marketing assets.
* **Download as Image:** Implemented functionality to download the generated HTML preview as a PNG image (using `html2canvas`).
* **Download Code:** Added buttons to download the generated raw HTML code or the full Vue.js project structure.

#### Backend (FastAPI)
* **Unified API Structure:** Created a structured API with routers for different functionalities (`/api/v1/marketing`, `/api/v1/webapp`).
* **Integrated "Full UI" Generation:** Ported and integrated the logic from the previous "dmi-ui-from-screenshot-backend" project to generate complete Vue.js apps from screenshots and text prompts.
* **Style & Context Extraction:** Implemented endpoints to analyze uploaded design files (images, PDFs) using Gemini Pro Vision to extract brand style guides (colors, fonts, spacing) and textual context.
* **Prompt Engineering:** Refined system prompts for different personas:
    * **"Brand Designer"** for creating visually striking HTML banners.
    * **"Frontend Architect"** for generating structured, functional Vue.js code.
* **Template Management:** Added a `templates/` directory to structure the output of generated Vue.js projects (e.g., `App.vue`, `main.js`).
* **CORS Configuration:** Configured Cross-Origin Resource Sharing (CORS) to allow communication between the React frontend and FastAPI backend.

### 🔧 Improvements & Fixes

* **Dependency Management:** Updated `requirements.txt` for the backend to include FastAPI, Uvicorn, Python-multipart, and Google Generative AI SDK.
* **Environment Variables:** Shifted to using `.env` files for managing sensitive API keys (Google Gemini API).
* **Project Structure:** Reorganized the entire codebase into distinct `frontend/`, `backend/`, and legacy `streamlit_app/` directories.
* **Documentation:** Added a comprehensive `README.md` outlining the project's purpose, architecture, setup instructions, and usage flows.
* **Git Ignore:** Added a `.gitignore` file to exclude virtual environments, node modules, environment variables, and other temporary files.

### 🎨 Assets

* **Project Logo:** Added the official "AlchemyStudio" logo to the repository.
* **Result Screenshots:** Included screenshots of the generated outputs and the application interface in the documentation.
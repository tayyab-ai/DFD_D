# Deepfake Detector Prototype

## Overview

This is a prototype web application for deepfake detection, designed for testing purposes with potential Discord bot integration. The application features a modern dark-themed interface that allows users to upload image, video, or audio files for analysis. Built with Flask backend and responsive frontend using Bootstrap, the system currently provides dummy detection results for testing the user interface and file upload functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple client-server architecture with a Flask web server handling file uploads and serving static content. The frontend is a single-page application with modern responsive design, while the backend provides RESTful endpoints for file processing.

### Frontend Architecture
- **Technology Stack**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5.3.0 for responsive design
- **Styling**: Custom CSS with dark theme and neon color palette
- **Fonts**: Google Fonts (Poppins) for typography
- **Animations**: Animate.css for smooth transitions
- **Icons**: Font Awesome 6.4.0 for iconography

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **File Handling**: Werkzeug for secure file uploads
- **Storage**: Temporary filesystem storage using Python's tempfile module
- **Logging**: Python's built-in logging module for debugging

## Key Components

### 1. File Upload System
- **Purpose**: Handle user file uploads for deepfake detection
- **Supported Formats**: Images (PNG, JPG, JPEG, GIF), Videos (MP4, AVI, MOV), Audio (MP3, WAV, OGG)
- **Size Limit**: 5MB maximum file size
- **Security**: Filename sanitization using Werkzeug's secure_filename

### 2. User Interface Components
- **Navigation Bar**: Fixed-top navigation with brand logo and section links
- **Hero Section**: Animated title section with call-to-action
- **Upload Form**: Drag-and-drop file upload interface
- **Results Display**: Card-based layout for showing detection results

### 3. Responsive Design System
- **Grid System**: Bootstrap's 12-column grid for layout
- **Breakpoints**: Mobile-first responsive design
- **Dark Theme**: Custom CSS variables for consistent theming

## Data Flow

1. **File Upload Process**:
   - User selects file through web interface
   - JavaScript validates file type and size client-side
   - File is submitted to Flask backend via POST request
   - Backend validates file extension and saves to temporary directory
   - Dummy detection results are generated and returned as JSON
   - Frontend displays results in styled cards

2. **Navigation Flow**:
   - Single-page application with smooth scrolling between sections
   - JavaScript handles navigation state and scroll effects
   - Responsive navbar adapts to screen size

## External Dependencies

### Frontend CDNs
- **Bootstrap 5.3.0**: UI framework and responsive grid
- **Google Fonts API**: Poppins font family
- **Animate.css 4.1.1**: CSS animation library
- **Font Awesome 6.4.0**: Icon library

### Python Packages
- **Flask**: Web framework for routing and templating
- **Werkzeug**: WSGI utilities and secure file handling
- **tempfile**: Temporary file storage (Python standard library)
- **logging**: Application logging (Python standard library)

## Deployment Strategy

### Environment Configuration
- **Session Secret**: Configurable via environment variable `SESSION_SECRET`
- **Upload Directory**: Uses system temporary directory by default
- **File Size Limits**: Configurable through Flask app config
- **Debug Mode**: Controlled via logging level configuration

### Hosting Requirements
- **Python 3.x**: Runtime environment
- **Web Server**: Flask development server (production would require WSGI server)
- **File System**: Write access to temporary directory for file uploads
- **Network**: HTTP/HTTPS capability for web serving

### Scalability Considerations
- Current implementation uses temporary file storage (not persistent)
- No database backend (stateless design)
- Client-side file validation reduces server load
- CDN-hosted assets reduce bandwidth requirements

The application is designed as a lightweight prototype suitable for testing deepfake detection workflows and user interface concepts, with the flexibility to integrate actual AI/ML detection models in the future.
// Deepfake Detector Prototype - JavaScript Functions

// Global variables
let isUploading = false;

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    console.log('Deepfake Detector initialized');
    initializeEventListeners();
    addSmoothScrolling();
});

// Initialize all event listeners
function initializeEventListeners() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }
    
    // Add navbar scroll effect
    window.addEventListener('scroll', handleNavbarScroll);
}

// Handle navbar scroll effect
function handleNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.backgroundColor = 'rgba(10, 10, 10, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.backgroundColor = 'rgba(10, 10, 10, 0.8)';
        navbar.style.backdropFilter = 'blur(5px)';
    }
}

// Add smooth scrolling to navigation links
function addSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 70; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Handle file selection and validation
function handleFileSelection(event) {
    const file = event.target.files[0];
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (file) {
        // Validate file size (50MB = 50 * 1024 * 1024 bytes)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            showError('File size must be less than 50MB. Please choose a smaller file.');
            event.target.value = '';
            return;
        }
        
        // Validate file type
        const allowedTypes = [
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif',
            'video/mp4', 'video/avi', 'video/quicktime',
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3', 'audio/m4a'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            showError('Invalid file type. Please upload an image, video, or audio file.');
            event.target.value = '';
            return;
        }
        
        // Update button text to show file is ready
        analyzeBtn.innerHTML = `<i class="fas fa-search me-2"></i>Analyze "${file.name}"`;
        analyzeBtn.disabled = false;
        
        console.log('File selected:', file.name, 'Size:', formatFileSize(file.size), 'Type:', file.type);
    } else {
        // Reset button if no file selected
        analyzeBtn.innerHTML = '<i class="fas fa-search me-2"></i>Analyze File';
        analyzeBtn.disabled = true;
    }
}

// Handle file upload and analysis
async function handleFileUpload(event) {
    event.preventDefault();
    
    if (isUploading) {
        console.log('Upload already in progress');
        return;
    }
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a file to analyze.');
        return;
    }
    
    isUploading = true;
    showLoadingSpinner();
    hideResults();
    
    try {
        // Create FormData object
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('Uploading file:', file.name);
        
        // Make API request
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showResults(result);
            console.log('Analysis complete:', result);
        } else {
            showError(result.error || 'An error occurred during analysis.');
            console.error('Upload error:', result);
        }
        
    } catch (error) {
        console.error('Network error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        hideLoadingSpinner();
        isUploading = false;
    }
}

// Show loading spinner
function showLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (spinner) {
        spinner.classList.remove('d-none');
    }
    
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    }
}

// Hide loading spinner
function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (spinner) {
        spinner.classList.add('d-none');
    }
    
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search me-2"></i>Analyze File';
    }
}

// Show analysis results
function showResults(data) {
    const resultsSection = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    
    if (!resultsSection || !resultContent) {
        console.error('Results elements not found');
        return;
    }
    
    // Determine result color based on confidence
    const confidence = Math.round(data.confidence * 100);
    let resultColor = 'success';
    let resultIcon = 'check-circle';
    
    if (confidence >= 70) {
        resultColor = 'danger';
        resultIcon = 'exclamation-triangle';
    } else if (confidence >= 40) {
        resultColor = 'warning';
        resultIcon = 'question-circle';
    }
    
    // Create result HTML
    resultContent.innerHTML = `
        <div class="result-item fadeInUp">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h4 class="text-${resultColor} mb-3">
                        <i class="fas fa-${resultIcon} me-2"></i>${data.result}
                    </h4>
                    <p class="mb-2"><strong>File:</strong> ${data.filename}</p>
                    <p class="mb-2"><strong>Type:</strong> ${data.file_type}</p>
                    <p class="mb-3"><strong>Confidence:</strong> ${confidence}%</p>
                    
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%"></div>
                    </div>
                </div>
                <div class="col-md-4 text-center">
                    <div class="result-badge">
                        <i class="fas fa-${getFileTypeIcon(data.file_type)} fa-4x text-primary mb-3"></i>
                        <h5 class="text-${resultColor}">${confidence}%</h5>
                        <small class="text-muted">Confidence Score</small>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-info mt-4" role="alert">
                <i class="fas fa-info-circle me-2"></i>
                ${data.message}
            </div>
        </div>
    `;
    
    // Show results section with animation
    resultsSection.classList.remove('d-none');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Add animation class
    setTimeout(() => {
        resultContent.classList.add('animate__animated', 'animate__fadeIn');
    }, 100);
}

// Hide results section
function hideResults() {
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        resultsSection.classList.add('d-none');
    }
}

// Get file type icon
function getFileTypeIcon(fileType) {
    switch (fileType.toLowerCase()) {
        case 'image':
            return 'image';
        case 'video':
            return 'video';
        case 'audio':
            return 'headphones';
        default:
            return 'file';
    }
}

// Show error message
function showError(message) {
    // Create error alert if it doesn't exist
    let errorAlert = document.getElementById('errorAlert');
    
    if (!errorAlert) {
        errorAlert = document.createElement('div');
        errorAlert.id = 'errorAlert';
        errorAlert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        errorAlert.style.cssText = 'top: 80px; right: 20px; z-index: 1050; max-width: 400px;';
        document.body.appendChild(errorAlert);
    }
    
    errorAlert.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Error:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (errorAlert && errorAlert.parentNode) {
            errorAlert.remove();
        }
    }, 5000);
    
    console.error('Error shown to user:', message);
}

// Reset form and hide results
function resetForm() {
    const uploadForm = document.getElementById('uploadForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (uploadForm) {
        uploadForm.reset();
    }
    
    if (analyzeBtn) {
        analyzeBtn.innerHTML = '<i class="fas fa-search me-2"></i>Analyze File';
        analyzeBtn.disabled = true;
    }
    
    hideResults();
    hideLoadingSpinner();
    isUploading = false;
    
    // Scroll back to upload section
    const uploadSection = document.getElementById('upload');
    if (uploadSection) {
        uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    console.log('Form reset');
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
    // Add parallax effect to hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero-section');
        if (hero) {
            hero.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

console.log('Deepfake Detector JavaScript loaded successfully');

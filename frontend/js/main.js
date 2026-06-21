// main.js
class HealthCareApp {
    constructor() {
        // Initialize state
        this.state = {
            user: null,
            isAuthenticated: false,
            isLoading: false,
            currentPage: 'dashboard',
            notifications: [],
            comparisonList: [],
            filters: {
                specialty: '',
                distance: '',
                rating: 0,
                sortBy: 'match'
            }
        };

        // DOM Elements
        this.elements = {};
        
        // Initialize app
        this.init();
    }

    // Initialize application
    init() {
        this.cacheElements();
        this.bindEvents();
        this.loadUserData();
        this.updateUI();
        this.setupServiceWorker();
    }

    // Cache DOM elements
    cacheElements() {
        // Common elements
        this.elements = {
            // Navigation
            navbar: document.querySelector('.navbar'),
            sidebar: document.querySelector('.sidebar'),
            navToggler: document.querySelector('.navbar-toggler'),
            navLinks: document.querySelectorAll('.nav-link'),
            sidebarLinks: document.querySelectorAll('.sidebar-menu a'),
            
            // Auth elements
            loginForm: document.getElementById('loginForm'),
            registerForm: document.getElementById('registerForm'),
            logoutBtn: document.getElementById('logoutBtn'),
            
            // Dashboard elements
            statsCards: document.querySelectorAll('.stat-card'),
            activityList: document.getElementById('activityList'),
            
            // Upload elements
            dropArea: document.getElementById('dropArea'),
            fileInput: document.getElementById('fileInput'),
            fileList: document.getElementById('fileList'),
            
            // Recommendations elements
            searchInput: document.getElementById('searchInput'),
            filterControls: document.querySelectorAll('.filter-control'),
            hospitalCards: document.getElementById('hospitalCards'),
            comparisonList: document.getElementById('comparisonList'),
            
            // Analytics elements
            timeFilterBtns: document.querySelectorAll('.filter-btn'),
            charts: document.querySelectorAll('.chart-container canvas'),
            
            // Modals
            modals: document.querySelectorAll('.modal'),
            modalCloses: document.querySelectorAll('.modal-close'),
            
            // Notifications
            notificationContainer: document.querySelector('.notification-container'),
            
            // Loading overlay
            loadingOverlay: document.getElementById('loadingOverlay')
        };
    }

    // Bind event listeners
    bindEvents() {
        // Navigation
        if (this.elements.navToggler) {
            this.elements.navToggler.addEventListener('click', () => this.toggleNavigation());
        }

        // Nav link clicks
        this.elements.navLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e));
        });

        // Sidebar link clicks
        this.elements.sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e));
        });

        // Window scroll
        window.addEventListener('scroll', () => this.handleScroll());

        // Auth forms
        if (this.elements.loginForm) {
            this.elements.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (this.elements.registerForm) {
            this.elements.registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        if (this.elements.logoutBtn) {
            this.elements.logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // File upload
        if (this.elements.dropArea) {
            this.elements.dropArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            this.elements.dropArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            this.elements.dropArea.addEventListener('drop', (e) => this.handleDrop(e));
        }

        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Filter changes
        this.elements.filterControls?.forEach(control => {
            control.addEventListener('change', () => this.applyFilters());
        });

        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('input', () => this.applyFilters());
        }

        // Time filter buttons
        this.elements.timeFilterBtns?.forEach(btn => {
            btn.addEventListener('click', (e) => this.setTimeFilter(e));
        });

        // Modal close buttons
        this.elements.modalCloses?.forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });

        // Click outside modal to close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });

        // Initialize charts if on analytics page
        if (window.location.pathname.includes('analytics')) {
            this.initCharts();
        }

        // Initialize maps if on recommendations page
        if (window.location.pathname.includes('recommendations')) {
            this.initMap();
        }
    }

    // Navigation handlers
    toggleNavigation() {
        const navbarNav = document.querySelector('.navbar-nav');
        navbarNav?.classList.toggle('show');
        
        const sidebar = document.querySelector('.sidebar');
        sidebar?.classList.toggle('show');
    }

    handleNavClick(e) {
        e.preventDefault();
        const target = e.currentTarget;
        const page = target.getAttribute('href')?.replace('.html', '') || 'dashboard';
        
        // Update active state
        this.elements.navLinks.forEach(link => link.classList.remove('active'));
        this.elements.sidebarLinks.forEach(link => link.classList.remove('active'));
        target.classList.add('active');
        
        // Update state
        this.state.currentPage = page;
        
        // Navigate to page
        if (page !== this.state.currentPage) {
            window.location.href = `${page}.html`;
        }
        
        // Close mobile navigation
        this.toggleNavigation();
    }

    handleScroll() {
        // Add scrolled class to navbar
        if (window.scrollY > 50) {
            this.elements.navbar?.classList.add('scrolled');
        } else {
            this.elements.navbar?.classList.remove('scrolled');
        }
        
        // Parallax effect for hero sections
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    }

    // Authentication handlers
    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        this.showLoading();
        
        try {
            // Simulate API call
            await this.simulateApiCall('/api/auth/login', data);
            
            // Update state
            this.state.user = {
                id: 1,
                name: data.email.split('@')[0],
                email: data.email,
                role: 'patient'
            };
            this.state.isAuthenticated = true;
            
            // Save to localStorage
            localStorage.setItem('user', JSON.stringify(this.state.user));
            localStorage.setItem('token', 'demo-token');
            
            // Show success message
            this.showNotification('Login successful!', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
            
        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Validate passwords match
        if (data.password !== data.confirmPassword) {
            this.showNotification('Passwords do not match', 'error');
            return;
        }
        
        this.showLoading();
        
        try {
            // Simulate API call
            await this.simulateApiCall('/api/auth/register', data);
            
            // Show success message
            this.showNotification('Registration successful! Please login.', 'success');
            
            // Clear form
            form.reset();
            
            // Redirect to login page
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
            
        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    handleLogout() {
        // Clear state
        this.state.user = null;
        this.state.isAuthenticated = false;
        
        // Clear localStorage
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        
        // Show message
        this.showNotification('Logged out successfully', 'info');
        
        // Redirect to home
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
    }

    // File upload handlers
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.elements.dropArea?.classList.add('active');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.elements.dropArea?.classList.remove('active');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.elements.dropArea?.classList.remove('active');
        
        const files = e.dataTransfer.files;
        this.handleFiles(files);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.handleFiles(files);
    }

    handleFiles(files) {
        if (!files.length) return;
        
        Array.from(files).forEach(file => {
            if (this.validateFile(file)) {
                this.uploadFile(file);
            }
        });
    }

    validateFile(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification(`File type ${file.type} not supported`, 'error');
            return false;
        }
        
        if (file.size > maxSize) {
            this.showNotification(`File size exceeds 10MB limit`, 'error');
            return false;
        }
        
        return true;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        this.showLoading();
        
        try {
            // Simulate upload
            await this.simulateApiCall('/api/upload', formData);
            
            // Add to file list
            this.addFileToList(file);
            
            // Show success message
            this.showNotification(`${file.name} uploaded successfully`, 'success');
            
            // Trigger AI analysis if on upload page
            if (window.location.pathname.includes('upload')) {
                this.analyzeWithAI();
            }
            
        } catch (error) {
            this.showNotification(`Failed to upload ${file.name}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    addFileToList(file) {
        if (!this.elements.fileList) return;
        
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file"></i>
                <div>
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn-icon" onclick="app.previewFile('${file.name}')">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon text-danger" onclick="app.removeFile(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        this.elements.fileList.appendChild(fileItem);
    }

    // Filters and search
    applyFilters() {
        const searchTerm = this.elements.searchInput?.value.toLowerCase() || '';
        const specialty = document.getElementById('specialtyFilter')?.value || '';
        const distance = document.getElementById('distanceFilter')?.value || '';
        const minRating = parseFloat(document.getElementById('ratingFilter')?.value) || 0;
        const sortBy = document.getElementById('sortFilter')?.value || 'match';
        
        // Update state
        this.state.filters = { searchTerm, specialty, distance, minRating, sortBy };
        
        // Filter hospital cards
        this.filterHospitalCards();
    }

    filterHospitalCards() {
        if (!this.elements.hospitalCards) return;
        
        const cards = this.elements.hospitalCards.querySelectorAll('.hospital-card');
        const filters = this.state.filters;
        
        cards.forEach(card => {
            const name = card.querySelector('.hospital-name').textContent.toLowerCase();
            const specialties = card.querySelector('.specialties-list').textContent.toLowerCase();
            const rating = parseFloat(card.querySelector('.rating-value').textContent);
            const distance = parseFloat(card.querySelector('.hospital-distance').textContent);
            
            let isVisible = true;
            
            // Apply filters
            if (filters.searchTerm && !name.includes(filters.searchTerm)) {
                isVisible = false;
            }
            
            if (filters.specialty && !specialties.includes(filters.specialty)) {
                isVisible = false;
            }
            
            if (filters.minRating && rating < filters.minRating) {
                isVisible = false;
            }
            
            if (filters.distance && distance > parseFloat(filters.distance)) {
                isVisible = false;
            }
            
            // Show/hide card
            card.style.display = isVisible ? '' : 'none';
        });
    }

    setTimeFilter(e) {
        const btn = e.currentTarget;
        const period = btn.dataset.period;
        
        // Update active button
        this.elements.timeFilterBtns?.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update charts with new data
        this.updateCharts(period);
    }

    // Charts and visualizations
    initCharts() {
        // Case Trend Chart
        const caseTrendCtx = document.getElementById('caseTrendChart');
        if (caseTrendCtx) {
            new Chart(caseTrendCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                    datasets: [
                        {
                            label: 'Cases Analyzed',
                            data: [1250, 1300, 1450, 1600, 1750, 1900, 2100],
                            borderColor: '#1976d2',
                            backgroundColor: 'rgba(25, 118, 210, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
        
        // Hospital Performance Chart
        const hospitalCtx = document.getElementById('hospitalChart');
        if (hospitalCtx) {
            new Chart(hospitalCtx, {
                type: 'bar',
                data: {
                    labels: ['City Hospital', 'Medicare', 'General', 'Specialty', 'Community'],
                    datasets: [
                        {
                            label: 'Success Rate',
                            data: [92, 88, 85, 90, 87],
                            backgroundColor: '#9c27b0'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }

    updateCharts(period) {
        // In a real app, this would fetch new data based on period
        console.log('Updating charts for period:', period);
        this.showNotification(`Loading ${period} data...`, 'info');
    }

    // Map initialization
    initMap() {
        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;
        
        // Simulate map initialization
        mapContainer.innerHTML = `
            <div style="width: 100%; height: 100%; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #6c757d;">
                <div style="text-align: center;">
                    <i class="fas fa-map-marked-alt" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>Interactive map would display here</p>
                </div>
            </div>
        `;
    }

    // AI Analysis
    async analyzeWithAI() {
        this.showLoading();
        
        try {
            // Simulate AI analysis
            await this.simulateApiCall('/api/ai/analyze', {});
            
            // Update UI with results
            this.updateAIAnalysis();
            
            this.showNotification('AI analysis complete!', 'success');
            
        } catch (error) {
            this.showNotification('AI analysis failed', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateAIAnalysis() {
        // Update AI analysis results in UI
        const confidenceValue = document.getElementById('confidenceValue');
        const confidenceFill = document.getElementById('confidenceFill');
        const aiResults = document.getElementById('aiResults');
        
        if (confidenceValue && confidenceFill) {
            const confidence = Math.floor(Math.random() * 30) + 70; // 70-100%
            confidenceValue.textContent = `${confidence}%`;
            confidenceFill.style.width = `${confidence}%`;
        }
        
        if (aiResults) {
            aiResults.innerHTML = `
                <div class="result-item highlight">
                    <div class="result-header">
                        <div class="result-title">Preliminary Diagnosis</div>
                        <div class="result-confidence">87%</div>
                    </div>
                    <div class="result-description">
                        Based on analysis, possible cardiovascular condition detected
                    </div>
                </div>
                <div class="result-item">
                    <div class="result-header">
                        <div class="result-title">Urgency Level</div>
                        <div class="result-confidence">85%</div>
                    </div>
                    <div class="result-description">
                        Medium priority - Schedule appointment within 48 hours
                    </div>
                </div>
            `;
        }
    }

    // Comparison functionality
    addToComparison(hospitalId) {
        // Add hospital to comparison list
        if (this.state.comparisonList.length >= 3) {
            this.showNotification('Maximum 3 hospitals can be compared', 'warning');
            return;
        }
        
        if (!this.state.comparisonList.includes(hospitalId)) {
            this.state.comparisonList.push(hospitalId);
            this.updateComparisonPanel();
            this.showNotification('Added to comparison', 'success');
        }
    }

    removeFromComparison(hospitalId) {
        this.state.comparisonList = this.state.comparisonList.filter(id => id !== hospitalId);
        this.updateComparisonPanel();
    }

    updateComparisonPanel() {
        if (!this.elements.comparisonList) return;
        
        // Update comparison list UI
        const count = document.getElementById('comparisonCount');
        if (count) {
            count.textContent = this.state.comparisonList.length;
        }
    }

    // Modal handlers
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal() {
        this.elements.modals?.forEach(modal => {
            modal.classList.remove('show');
        });
        document.body.style.overflow = '';
    }

    // Utility methods
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async simulateApiCall(endpoint, data) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Simulate different responses based on endpoint
        switch (endpoint) {
            case '/api/auth/login':
                if (data.email && data.password) {
                    return { success: true, token: 'demo-token', user: data.email };
                }
                throw new Error('Invalid credentials');
                
            case '/api/auth/register':
                if (data.email && data.password) {
                    return { success: true };
                }
                throw new Error('Registration failed');
                
            case '/api/upload':
                return { success: true, url: 'demo-url' };
                
            case '/api/ai/analyze':
                return { success: true, confidence: 87 };
                
            default:
                return { success: true };
        }
    }

    showNotification(message, type = 'info') {
        const types = {
            info: { icon: 'info-circle', color: 'var(--info)' },
            success: { icon: 'check-circle', color: 'var(--success)' },
            warning: { icon: 'exclamation-triangle', color: 'var(--warning)' },
            error: { icon: 'exclamation-circle', color: 'var(--danger)' }
        };
        
        const { icon, color } = types[type] || types.info;
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'toast';
        notification.innerHTML = `
            <div class="toast-header">
                <i class="fas fa-${icon}" style="color: ${color}; margin-right: 0.5rem;"></i>
                <strong class="mr-auto">${type.toUpperCase()}</strong>
                <button type="button" class="close" onclick="this.parentElement.parentElement.remove()">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        // Add to container or body
        const container = this.elements.notificationContainer || document.body;
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    showLoading() {
        this.state.isLoading = true;
        this.elements.loadingOverlay?.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    hideLoading() {
        this.state.isLoading = false;
        this.elements.loadingOverlay?.classList.remove('show');
        document.body.style.overflow = '';
    }

    // Load user data from localStorage
    loadUserData() {
        const userData = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        
        if (userData && token) {
            this.state.user = JSON.parse(userData);
            this.state.isAuthenticated = true;
        }
    }

    // Update UI based on state
    updateUI() {
        // Update user display
        const userElements = document.querySelectorAll('.user-info');
        userElements.forEach(element => {
            if (this.state.user) {
                element.textContent = this.state.user.name || this.state.user.email;
            }
        });
        
        // Update auth buttons visibility
        const authButtons = document.querySelectorAll('.auth-buttons');
        authButtons.forEach(container => {
            if (this.state.isAuthenticated) {
                container.innerHTML = `
                    <button class="btn btn-outline" id="logoutBtn">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </button>
                `;
                document.getElementById('logoutBtn')?.addEventListener('click', () => this.handleLogout());
            }
        });
    }

    // Service Worker setup
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').then(
                    registration => {
                        console.log('ServiceWorker registration successful');
                    },
                    error => {
                        console.log('ServiceWorker registration failed:', error);
                    }
                );
            });
        }
    }

    // Public methods for HTML onclick handlers
    previewFile(fileName) {
        this.openModal('previewModal');
        // Load file preview logic here
    }

    removeFile(button) {
        const fileItem = button.closest('.file-item');
        if (fileItem) {
            fileItem.remove();
        }
    }

    bookAppointment(hospitalId) {
        this.openModal('appointmentModal');
        // Load hospital details for booking
    }

    generateNewRecommendations() {
        this.showLoading();
        setTimeout(() => {
            this.showNotification('New AI recommendations generated!', 'success');
            this.hideLoading();
        }, 2000);
    }

    compareHospitals() {
        if (this.state.comparisonList.length < 2) {
            this.showNotification('Select at least 2 hospitals to compare', 'error');
            return;
        }
        
        this.openModal('comparisonModal');
        // Load comparison data
    }

    downloadReport(type) {
        this.showNotification(`Downloading ${type} report...`, 'info');
        // Implement download logic
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new HealthCareApp();
});

// Export for module usage (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HealthCareApp;
}
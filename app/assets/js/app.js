/**
 * RFM Insights - Main Application
 * 
 * This module initializes the application and handles global functionality
 */

class App {
    constructor() {
        this.stateManager = window.stateManager;
        this.apiClient = window.apiClient;
        this.config = window.appConfig;
        this.notificationManager = null;
        this.sidebar = null;
        this.userProfile = null;
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    init() {
        // Initialize API client
        this.apiClient = window.apiClient || new APIClient();
        window.apiClient = this.apiClient;
        
        // Initialize state manager
        this.stateManager = window.stateManager || new StateManager();
        window.stateManager = this.stateManager;
        
        // Initialize notification manager
        this.notificationManager = window.notificationManager || new NotificationManager();
        window.notificationManager = this.notificationManager;
        
        // Initialize sidebar
        this.sidebar = document.getElementById('sidebar');
        this.initSidebar();
        
        // Initialize user profile
        this.userProfile = document.getElementById('user-profile');
        this.initUserProfile();
        
        // Initialize logout button
        this.initLogout();
        
        // Check authentication
        this.checkAuthentication();
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Subscribe to state changes
        this.stateManager.subscribe(this.handleStateChange.bind(this));
    }
    
    /**
     * Initialize sidebar functionality
     */
    initSidebar() {
        if (!this.sidebar) return;
        
        // Toggle sidebar on mobile
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.body.classList.toggle('sidebar-collapsed');
            });
        }
        
        // Set active menu item based on current page
        const currentPage = this.stateManager.getState().currentPage;
        const menuItems = this.sidebar.querySelectorAll('.sidebar-item');
        
        menuItems.forEach(item => {
            const itemPage = item.dataset.page;
            if (itemPage === currentPage) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    /**
     * Initialize user profile dropdown
     */
    initUserProfile() {
        if (!this.userProfile) return;
        
        this.userProfile.addEventListener('click', () => {
            this.userProfile.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!this.userProfile.contains(event.target)) {
                this.userProfile.classList.remove('active');
            }
        });
    }
    
    /**
     * Initialize logout button
     */
    initLogout() {
        const logoutBtn = document.getElementById('logout-btn');
        if (!logoutBtn) return;
        
        logoutBtn.addEventListener('click', (event) => {
            event.preventDefault();
            this.logout();
        });
    }
    
    /**
     * Check if user is authenticated
     */
    checkAuthentication() {
        const isAuthenticated = this.stateManager.getState().isAuthenticated;
        const isLoginPage = window.location.pathname.includes('login.html');
        const isCadastroPage = window.location.pathname.includes('cadastro.html');
        
        // Redirect to login if not authenticated and not on login/register page
        if (!isAuthenticated && !isLoginPage && !isCadastroPage) {
            window.location.href = '/login.html';
        }
        
        // Redirect to dashboard if authenticated and on login/register page
        if (isAuthenticated && (isLoginPage || isCadastroPage)) {
            window.location.href = '/index.html';
        }
    }
    
    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }

        // RFM Analysis form
        const rfmForm = document.getElementById('rfmForm');
        if (rfmForm) {
            rfmForm.addEventListener('submit', this.handleRfmAnalysis.bind(this));
        }

        // Message generation form
        const messageForm = document.getElementById('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', this.handleMessageGeneration.bind(this));
        }

        // Insight generation form
        const insightForm = document.getElementById('insightForm');
        if (insightForm) {
            insightForm.addEventListener('submit', this.handleInsightGeneration.bind(this));
        }
    }
    
    /**
     * Handle state change
     * @param {Object} state - Application state
     */
    handleStateChange(state) {
        // Update UI based on state changes
        this.updateUI(state);
    }
    
    /**
     * Update UI based on state
     * @param {Object} state - Application state
     */
    updateUI(state) {
        // Update user profile
        if (this.userProfile) {
            const userName = state.user ? state.user.full_name : 'Usuário';
            const userNameElement = this.userProfile.querySelector('.user-name');
            if (userNameElement) {
                userNameElement.textContent = userName;
            }
        }
        
        // Update page title
        const pageTitle = document.getElementById('page-title');
        if (pageTitle) {
            let title = 'Dashboard';
            
            switch (state.currentPage) {
                case 'analise':
                    title = 'Análise RFM';
                    break;
                case 'marketplace':
                    title = 'Geração de Mensagens';
                    break;
                case 'integracao':
                    title = 'Integrações';
                    break;
                case 'configuracoes':
                    title = 'Configurações';
                    break;
            }
            
            pageTitle.textContent = title;
        }
        
        // Show/hide loading indicator
        this.toggleLoading(state.loading);
        
        // Update loading indicators
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(element => {
            element.style.display = state.loading ? 'block' : 'none';
        });

        // Update error messages
        const errorElement = document.getElementById('errorMessage');
        if (errorElement) {
            errorElement.textContent = state.error || '';
            errorElement.style.display = state.error ? 'block' : 'none';
        }

        // Update authentication UI
        const authElements = document.querySelectorAll('.auth-only');
        authElements.forEach(element => {
            element.style.display = state.isAuthenticated ? 'block' : 'none';
        });

        // Update user information
        const userElement = document.getElementById('userInfo');
        if (userElement && state.user) {
            userElement.textContent = `Welcome, ${state.user.name}`;
        }
    }
    
    /**
     * Toggle loading indicator
     * @param {boolean} isLoading - Loading state
     */
    toggleLoading(isLoading) {
        let loadingIndicator = document.getElementById('loading-indicator');
        
        if (isLoading) {
            if (!loadingIndicator) {
                loadingIndicator = document.createElement('div');
                loadingIndicator.id = 'loading-indicator';
                loadingIndicator.className = 'loading-indicator';
                loadingIndicator.innerHTML = '<div class="spinner"></div>';
                document.body.appendChild(loadingIndicator);
            }
            loadingIndicator.classList.add('active');
        } else if (loadingIndicator) {
            loadingIndicator.classList.remove('active');
        }
    }
    
    /**
     * Logout user
     */
    logout() {
        // Clear authentication
        this.apiClient.clearToken();
        this.stateManager.clearUser();
        
        // Show notification
        this.notificationManager.success('Logout', 'Você foi desconectado com sucesso.');
        
        // Redirect to login page
        window.location.href = '/login.html';
    }

    async handleLogin(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const credentials = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            await this.stateManager.login(credentials);
            this.showNotification('Login successful!', 'success');
            this.redirectToDashboard();
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async handleRfmAnalysis(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = {
            file: formData.get('file'),
            parameters: {
                recencyWeight: parseFloat(formData.get('recencyWeight')),
                frequencyWeight: parseFloat(formData.get('frequencyWeight')),
                monetaryWeight: parseFloat(formData.get('monetaryWeight'))
            }
        };

        try {
            const result = await this.stateManager.analyzeRFM(data);
            this.displayRfmResults(result);
            this.showNotification('RFM analysis completed successfully!', 'success');
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async handleMessageGeneration(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = {
            segment: formData.get('segment'),
            tone: formData.get('tone'),
            length: formData.get('length')
        };

        try {
            const message = await this.stateManager.generateMessage(data);
            this.displayMessage(message);
            this.showNotification('Message generated successfully!', 'success');
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async handleInsightGeneration(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = {
            segment: formData.get('segment'),
            metric: formData.get('metric'),
            timeframe: formData.get('timeframe')
        };

        try {
            const insight = await this.stateManager.generateInsight(data);
            this.displayInsight(insight);
            this.showNotification('Insight generated successfully!', 'success');
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    redirectToDashboard() {
        window.location.href = '/dashboard.html';
    }

    displayRfmResults(result) {
        const resultsContainer = document.getElementById('rfmResults');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <h3>RFM Analysis Results</h3>
                <div class="results-grid">
                    ${this.generateRfmResultsHtml(result)}
                </div>
            `;
        }
    }

    displayMessage(message) {
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer) {
            const messageElement = document.createElement('div');
            messageElement.className = 'message';
            messageElement.innerHTML = `
                <h4>${message.title}</h4>
                <p>${message.content}</p>
                <div class="message-meta">
                    <span>Segment: ${message.segment}</span>
                    <span>Tone: ${message.tone}</span>
                </div>
            `;
            messagesContainer.appendChild(messageElement);
        }
    }

    displayInsight(insight) {
        const insightsContainer = document.getElementById('insightsContainer');
        if (insightsContainer) {
            const insightElement = document.createElement('div');
            insightElement.className = 'insight';
            insightElement.innerHTML = `
                <h4>${insight.title}</h4>
                <p>${insight.content}</p>
                <div class="insight-meta">
                    <span>Segment: ${insight.segment}</span>
                    <span>Metric: ${insight.metric}</span>
                </div>
            `;
            insightsContainer.appendChild(insightElement);
        }
    }

    generateRfmResultsHtml(result) {
        return `
            <div class="result-card">
                <h4>Customer Segments</h4>
                <ul>
                    ${Object.entries(result.segments).map(([segment, count]) => `
                        <li>${segment}: ${count} customers</li>
                    `).join('')}
                </ul>
            </div>
            <div class="result-card">
                <h4>Key Metrics</h4>
                <ul>
                    <li>Average Recency: ${result.metrics.avgRecency} days</li>
                    <li>Average Frequency: ${result.metrics.avgFrequency}</li>
                    <li>Average Monetary: $${result.metrics.avgMonetary.toFixed(2)}</li>
                </ul>
            </div>
            <div class="result-card">
                <h4>Recommendations</h4>
                <ul>
                    ${result.recommendations.map(rec => `
                        <li>${rec}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
/**
 * RFM Insights - Main Application
 * 
 * This module initializes the application and handles global functionality
 */

class App {
    constructor() {
        this.apiClient = null;
        this.stateManager = null;
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
        
        // Subscribe to state changes
        this.stateManager.subscribe(state => {
            this.updateUI(state);
        });
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
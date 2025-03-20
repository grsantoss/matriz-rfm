// AI Insights Module for RFM Analysis

class AIInsights {
    constructor() {
        this.apiEndpoint = '/api/ai-insights';
        this.generateBtn = document.getElementById('generate-insights-btn');
        this.aiSuggestionsContent = document.getElementById('ai-suggestions-content');
        this.aiLoading = document.getElementById('ai-loading');
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Add click event to generate insights button
        if (this.generateBtn) {
            this.generateBtn.addEventListener('click', () => this.generateInsights());
        }
    }
    
    /**
     * Generate AI insights based on RFM analysis data
     */
    async generateInsights() {
        // Check if RFM data is available
        if (!window.rfmData || !window.rfmData.segments) {
            this.showError('Por favor, realize a análise RFM antes de gerar insights.');
            return;
        }
        
        // Show loading state
        this.showLoading(true);
        
        try {
            // Get business segment type
            const businessType = document.getElementById('segment-select').value || 'ecommerce';
            
            // Prepare data for API request
            const requestData = {
                business_type: businessType,
                rfm_data: window.rfmData,
                insight_type: 'general' // Can be 'general', 'segment_specific', or 'business_specific'
            };
            
            // Call API to generate insights
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`Erro na API: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display insights
            this.displayInsights(data.insights);
        } catch (error) {
            console.error('Erro ao gerar insights:', error);
            this.showError('Ocorreu um erro ao gerar insights. Por favor, tente novamente.');
        } finally {
            // Hide loading state
            this.showLoading(false);
        }
    }
    
    /**
     * Display AI generated insights
     * @param {String} insights - The insights text
     */
    displayInsights(insights) {
        if (!this.aiSuggestionsContent) return;
        
        // Create insights container
        const insightsHtml = `
            <div class="ai-insights-container">
                <div class="ai-header d-flex align-items-center mb-3">
                    <div class="ai-avatar me-2">
                        <i class="fas fa-robot text-primary"></i>
                    </div>
                    <div class="ai-title">
                        <h6 class="mb-0">Insights Estratégicos</h6>
                        <small class="text-muted">Gerado por IA</small>
                    </div>
                </div>
                <div class="ai-content">
                    ${this.formatInsightsText(insights)}
                </div>
            </div>
        `;
        
        this.aiSuggestionsContent.innerHTML = insightsHtml;
    }
    
    /**
     * Format insights text with Markdown-like formatting
     * @param {String} text - The raw insights text
     * @returns {String} - Formatted HTML
     */
    formatInsightsText(text) {
        if (!text) return '';
        
        // Convert line breaks to paragraphs
        let formatted = text.replace(/\n\n/g, '</p><p>');
        formatted = `<p>${formatted}</p>`;
        
        // Convert bullet points
        formatted = formatted.replace(/- ([^\n]+)/g, '<li>$1</li>');
        formatted = formatted.replace(/<li>/g, '<ul><li>').replace(/<\/li>\n/g, '</li></ul>');
        
        // Convert headers
        formatted = formatted.replace(/## ([^\n]+)/g, '<h5>$1</h5>');
        formatted = formatted.replace(/# ([^\n]+)/g, '<h4>$1</h4>');
        
        // Convert bold text
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        return formatted;
    }
    
    /**
     * Show or hide loading state
     * @param {Boolean} isLoading - Whether to show or hide loading
     */
    showLoading(isLoading) {
        if (!this.aiSuggestionsContent || !this.aiLoading) return;
        
        if (isLoading) {
            this.aiSuggestionsContent.classList.add('d-none');
            this.aiLoading.classList.remove('d-none');
        } else {
            this.aiSuggestionsContent.classList.remove('d-none');
            this.aiLoading.classList.add('d-none');
        }
    }
    
    /**
     * Show error message
     * @param {String} message - Error message to display
     */
    showError(message) {
        if (!this.aiSuggestionsContent) return;
        
        const errorHtml = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
            </div>
        `;
        
        this.aiSuggestionsContent.innerHTML = errorHtml;
    }
}

// Initialize AI Insights when document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.aiInsights = new AIInsights();
});
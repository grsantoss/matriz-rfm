/**
 * RFM Insights - Dashboard Module
 * 
 * This module handles the dashboard functionality
 */

class Dashboard {
    constructor() {
        this.statsElements = {
            rfmCount: document.getElementById('rfm-count'),
            messageCount: document.getElementById('message-count'),
            customerCount: document.getElementById('customer-count'),
            insightCount: document.getElementById('insight-count')
        };
        
        this.recentAnalysesList = document.getElementById('recent-analyses-list');
        this.segmentsChart = null;
        
        this.init();
    }
    
    /**
     * Initialize the dashboard
     */
    init() {
        // Subscribe to state changes
        if (window.stateManager) {
            window.stateManager.subscribe(state => {
                this.updateStats(state.dashboardStats);
            });
        }
        
        // Load dashboard data
        this.loadDashboardData();
        
        // Initialize charts
        this.initCharts();
    }
    
    /**
     * Load dashboard data from API
     */
    async loadDashboardData() {
        try {
            if (!window.apiClient) return;
            
            // Show loading state
            if (window.stateManager) {
                window.stateManager.setLoading(true);
            }
            
            // Get analysis history
            const history = await window.apiClient.getAnalysisHistory(5);
            this.updateRecentAnalyses(history);
            
            // Get dashboard stats
            const stats = {
                rfmCount: history.length || 0,
                messageCount: 0,
                customerCount: 0,
                insightCount: 0
            };
            
            // Calculate total customers from history
            if (history && history.length > 0) {
                stats.customerCount = history.reduce((total, item) => {
                    return total + (item.record_count || 0);
                }, 0);
            }
            
            // Get messages count
            try {
                const messages = await window.apiClient.getUserMessages(1, 0);
                stats.messageCount = messages.total || 0;
            } catch (error) {
                console.error('Error loading messages count:', error);
            }
            
            // Update stats in state
            if (window.stateManager) {
                window.stateManager.updateDashboardStats(stats);
            } else {
                this.updateStats(stats);
            }
            
            // Hide loading state
            if (window.stateManager) {
                window.stateManager.setLoading(false);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            
            // Show error notification
            if (window.notificationManager) {
                window.notificationManager.error(
                    'Erro ao carregar dados',
                    'Não foi possível carregar os dados do dashboard.'
                );
            }
            
            // Hide loading state
            if (window.stateManager) {
                window.stateManager.setLoading(false);
            }
        }
    }
    
    /**
     * Update dashboard statistics
     * @param {Object} stats - Dashboard statistics
     */
    updateStats(stats) {
        // Update stats elements
        if (this.statsElements.rfmCount) {
            this.statsElements.rfmCount.textContent = stats.rfmCount || 0;
        }
        
        if (this.statsElements.messageCount) {
            this.statsElements.messageCount.textContent = stats.messageCount || 0;
        }
        
        if (this.statsElements.customerCount) {
            this.statsElements.customerCount.textContent = stats.customerCount || 0;
        }
        
        if (this.statsElements.insightCount) {
            this.statsElements.insightCount.textContent = stats.insightCount || 0;
        }
    }
    
    /**
     * Update recent analyses list
     * @param {Array} analyses - Recent analyses
     */
    updateRecentAnalyses(analyses) {
        if (!this.recentAnalysesList) return;
        
        // Clear list
        this.recentAnalysesList.innerHTML = '';
        
        // Add analyses to list
        if (analyses && analyses.length > 0) {
            analyses.forEach(analysis => {
                const li = document.createElement('li');
                li.className = 'recent-analysis-item';
                
                const date = new Date(analysis.timestamp);
                const formattedDate = date.toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
                
                li.innerHTML = `
                    <div class="analysis-info">
                        <h5>${analysis.filename}</h5>
                        <p>${analysis.segment_type} - ${formattedDate}</p>
                    </div>
                    <div class="analysis-stats">
                        <span class="badge bg-primary">${analysis.record_count} clientes</span>
                    </div>
                `;
                
                this.recentAnalysesList.appendChild(li);
            });
        } else {
            // Show no data message
            const li = document.createElement('li');
            li.className = 'no-data';
            li.textContent = 'Nenhuma análise recente';
            this.recentAnalysesList.appendChild(li);
        }
    }
    
    /**
     * Initialize dashboard charts
     */
    initCharts() {
        // Initialize RFM segments chart
        const segmentsChartCanvas = document.getElementById('rfm-segments-chart');
        if (segmentsChartCanvas) {
            this.segmentsChart = new Chart(segmentsChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Campeões', 'Leais', 'Potenciais', 'Novos', 'Em Risco', 'Hibernando', 'Perdidos'],
                    datasets: [{
                        data: [0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#4CAF50', // Champions
                            '#2196F3', // Loyal
                            '#9C27B0', // Potential
                            '#00BCD4', // New
                            '#FFC107', // At Risk
                            '#FF9800', // Hibernating
                            '#F44336'  // Lost
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    /**
     * Update segments chart with data
     * @param {Object} segmentCounts - Segment counts
     */
    updateSegmentsChart(segmentCounts) {
        if (!this.segmentsChart) return;
        
        // Map segment names to chart labels
        const segmentMapping = {
            'champions': 0,      // Campeões
            'loyal': 1,          // Leais
            'potential': 2,      // Potenciais
            'new_customers': 3,  // Novos
            'at_risk': 4,        // Em Risco
            'hibernating': 5,    // Hibernando
            'lost': 6            // Perdidos
        };
        
        // Create data array with zeros
        const data = [0, 0, 0, 0, 0, 0, 0];
        
        // Fill data from segment counts
        Object.entries(segmentCounts).forEach(([segment, count]) => {
            const index = segmentMapping[segment.toLowerCase()];
            if (index !== undefined) {
                data[index] = count;
            }
        });
        
        // Update chart data
        this.segmentsChart.data.datasets[0].data = data;
        this.segmentsChart.update();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
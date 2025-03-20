/**
 * RFM Insights - Charts Module
 * This module handles the visualization of RFM analysis and predictive analytics data
 */

// Import Chart.js if not already included in the HTML
if (typeof Chart === 'undefined') {
    const chartScript = document.createElement('script');
    chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
    document.head.appendChild(chartScript);
}

// Import D3.js for Treemap
if (typeof d3 === 'undefined') {
    const d3Script = document.createElement('script');
    d3Script.src = 'https://d3js.org/d3.v7.min.js';
    document.head.appendChild(d3Script);
}

/**
 * RFM Charts Class
 * Handles the creation and updating of all charts for RFM analysis
 */
class RFMCharts {
    constructor() {
        this.treemapChart = null;
        this.polarAreaChart = null;
        this.predictiveChart = null;
        this.chartColors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#8AC249', '#EA526F', '#00A6A6', '#605B56',
            '#837A75', '#ACC12F', '#9DACFF', '#5603AD', '#8367C7'
        ];
        
        // Segment color mapping
        this.segmentColors = {
            'Campeões': '#FF6384',
            'Clientes Fiéis': '#36A2EB',
            'Fiéis em Potencial': '#FFCE56',
            'Novos Clientes': '#4BC0C0',
            'Clientes Promissores': '#9966FF',
            'Clientes que Precisam de Atenção': '#FF9F40',
            'Clientes Quase Dormentes': '#8AC249',
            'Clientes que Não Posso Perder': '#EA526F',
            'Clientes em Risco': '#00A6A6',
            'Clientes Hibernando': '#605B56',
            'Clientes Perdidos': '#837A75'
        };
    }
    
    /**
     * Create RFM Treemap visualization
     * @param {Object} data - Treemap data from RFM analysis
     * @param {String} elementId - ID of the HTML element to render the chart
     */
    createTreemap(data, elementId = 'rfm-treemap') {
        // Clear previous chart if exists
        const container = document.getElementById(elementId);
        if (!container) return;
        
        container.innerHTML = '';
        
        // Set dimensions
        const width = container.clientWidth;
        const height = 400;
        
        // Create SVG
        const svg = d3.select(`#${elementId}`)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Prepare data for treemap
        const root = d3.hierarchy({children: data})
            .sum(d => d.customer_count)
            .sort((a, b) => b.value - a.value);
        
        // Create treemap layout
        d3.treemap()
            .size([width, height])
            .padding(2)
            (root);
        
        // Create tooltip
        const tooltip = d3.select('body')
            .append('div')
            .attr('class', 'treemap-tooltip')
            .style('position', 'absolute')
            .style('background-color', 'white')
            .style('border', '1px solid #ddd')
            .style('border-radius', '4px')
            .style('padding', '10px')
            .style('opacity', 0);
        
        // Add rectangles for each segment
        const cell = svg.selectAll('g')
            .data(root.leaves())
            .enter().append('g')
            .attr('transform', d => `translate(${d.x0},${d.y0})`);
        
        cell.append('rect')
            .attr('width', d => d.x1 - d.x0)
            .attr('height', d => d.y1 - d.y0)
            .attr('fill', d => this.segmentColors[d.data.segment] || this.chartColors[d.index % this.chartColors.length])
            .attr('stroke', '#fff')
            .on('mouseover', (event, d) => {
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                tooltip.html(
                    `<strong>${d.data.segment}</strong><br/>
                     Clientes: ${d.data.customer_count} (${d.data.customer_percentage}%)<br/>
                     Valor Total: R$ ${d.data.total_value.toLocaleString('pt-BR', {minimumFractionDigits: 2})}<br/>
                     Valor %: ${d.data.value_percentage}%`
                )
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });
        
        // Add text labels
        cell.append('text')
            .attr('x', 5)
            .attr('y', 15)
            .text(d => d.data.segment)
            .attr('font-size', '12px')
            .attr('fill', 'white');
        
        // Add legend
        const legend = svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(10, ${height - 100})`);
        
        const legendItems = legend.selectAll('.legend-item')
            .data(data)
            .enter().append('g')
            .attr('class', 'legend-item')
            .attr('transform', (d, i) => `translate(0, ${i * 20})`);
        
        legendItems.append('rect')
            .attr('width', 15)
            .attr('height', 15)
            .attr('fill', d => this.segmentColors[d.segment] || this.chartColors[data.indexOf(d) % this.chartColors.length]);
        
        legendItems.append('text')
            .attr('x', 20)
            .attr('y', 12)
            .text(d => d.segment)
            .attr('font-size', '10px');
    }
    
    /**
     * Create Polar Area Chart for segment distribution
     * @param {Object} data - Polar area data from RFM analysis
     * @param {String} elementId - ID of the HTML element to render the chart
     */
    createPolarAreaChart(data, elementId = 'segment-distribution') {
        // Get canvas element
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        // Destroy previous chart if exists
        if (this.polarAreaChart) {
            this.polarAreaChart.destroy();
        }
        
        // Prepare data for chart
        const labels = data.map(item => item.segment);
        const values = data.map(item => item.count);
        const backgroundColors = data.map(item => 
            this.segmentColors[item.segment] || this.chartColors[data.indexOf(item) % this.chartColors.length]
        );
        
        // Create chart
        this.polarAreaChart = new Chart(canvas, {
            type: 'polarArea',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
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
                                size: 10
                            },
                            boxWidth: 10
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = data[context.dataIndex];
                                return ` ${item.count} clientes (${item.percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Create Predictive Analytics Matrix Chart
     * @param {Object} data - Predictive analytics data
     * @param {String} elementId - ID of the HTML element to render the chart
     */
    createPredictiveChart(data, elementId = 'predictive-matrix') {
        // Get canvas element
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        // Destroy previous chart if exists
        if (this.predictiveChart) {
            this.predictiveChart.destroy();
        }
        
        // Extract insights data
        const insights = data.insights;
        
        // Create chart data
        const chartData = {
            labels: ['Retenção', 'Upsell', 'Cross-sell', 'LTV'],
            datasets: [{
                label: 'Oportunidades',
                data: [
                    insights.high_value_at_risk_count,
                    insights.upsell_targets_count,
                    insights.crosssell_targets_count,
                    Object.values(insights.segment_ltv_ranking)[0] // Highest LTV segment value
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        };
        
        // Create chart
        this.predictiveChart = new Chart(canvas, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de Clientes'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Categorias de Análise Preditiva'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const category = context.label;
                                
                                if (category === 'Retenção') {
                                    return `${value} clientes de alto valor em risco`;
                                } else if (category === 'Upsell') {
                                    return `${value} oportunidades de upsell`;
                                } else if (category === 'Cross-sell') {
                                    return `${value} oportunidades de cross-sell`;
                                } else if (category === 'LTV') {
                                    return `R$ ${value.toFixed(2)} valor médio do melhor segmento`;
                                }
                                return `${value}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Update all charts with new data
     * @param {Object} analysisResults - Complete results from RFM analysis API
     */
    updateAllCharts(analysisResults) {
        const rfmAnalysis = analysisResults.rfm_analysis;
        const predictiveAnalytics = analysisResults.predictive_analytics;
        
        // Update RFM Treemap
        this.createTreemap(rfmAnalysis.treemap_data, 'rfm-treemap');
        
        // Update Segment Distribution Polar Area Chart
        this.createPolarAreaChart(rfmAnalysis.polar_area_data, 'segment-distribution');
        
        // Update Predictive Analytics Chart
        this.createPredictiveChart(predictiveAnalytics, 'predictive-matrix');
        
        // Update statistics cards
        this.updateStatCards(analysisResults);
        
        // Update recommendations
        this.updateRecommendations(predictiveAnalytics.insights);
        
        // Update analysis date
        const analysisDate = new Date(historyEntry.timestamp);
        const formattedDate = analysisDate.toLocaleDateString('pt-BR');
        document.querySelectorAll('.small.text-muted').forEach(el => {
            el.textContent = `Última análise: ${formattedDate}`;
        });
    }
    
    /**
     * Update statistics cards with analysis results
     * @param {Object} analysisResults - Complete results from RFM analysis API
     */
    updateStatCards(analysisResults) {
        const rfmAnalysis = analysisResults.rfm_analysis;
        const segmentCounts = rfmAnalysis.segment_counts;
        const historyEntry = analysisResults.history_entry;
        
        // Total customers analyzed
        const totalCustomers = historyEntry.record_count;
        document.querySelector('.stat-card:nth-child(1) .value').textContent = totalCustomers.toLocaleString('pt-BR');
        
        // Loyal/Promising customers
        const loyalCount = (segmentCounts['Clientes Fiéis'] || 0) + 
                          (segmentCounts['Campeões'] || 0) + 
                          (segmentCounts['Clientes Promissores'] || 0) + 
                          (segmentCounts['Fiéis em Potencial'] || 0);
        document.querySelector('.stat-card:nth-child(2) .value').textContent = loyalCount.toLocaleString('pt-BR');
        
        // Customers needing attention
        const attentionCount = (segmentCounts['Clientes que Precisam de Atenção'] || 0) + 
                              (segmentCounts['Clientes Quase Dormentes'] || 0) + 
                              (segmentCounts['Clientes em Risco'] || 0);
        document.querySelector('.stat-card:nth-child(3) .value').textContent = attentionCount.toLocaleString('pt-BR');
        
        // Lost customers
        const lostCount = (segmentCounts['Clientes Perdidos'] || 0) + 
                         (segmentCounts['Clientes Hibernando'] || 0);
        document.querySelector('.stat-card:nth-child(4) .value').textContent = lostCount.toLocaleString('pt-BR');
        
        // Update analysis date
        const analysisDate = new Date(historyEntry.timestamp);
        const formattedDate = analysisDate.toLocaleDateString('pt-BR');
        document.querySelectorAll('.stat-card .small.text-muted').forEach(el => {
            el.textContent = `Última análise: ${formattedDate}`;
        });
    }
    
    /**
     * Update recommendations based on predictive insights
     * @param {Object} insights - Predictive insights data
     */
    updateRecommendations(insights) {
        // Create recommendations container if it doesn't exist
        let recommendationsContainer = document.getElementById('ai-recommendations');
        if (!recommendationsContainer) {
            const resultsSection = document.querySelector('.card-header:contains("Resultados da Análise")').closest('.card');
            recommendationsContainer = document.createElement('div');
            recommendationsContainer.id = 'ai-recommendations';
            recommendationsContainer.className = 'card mb-4';
            recommendationsContainer.innerHTML = `
                <div class="card-header">Sugestões de IA</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6 class="mb-3">Retenção de Clientes</h6>
                            <ul class="recommendations-list retention-list"></ul>
                        </div>
                        <div class="col-md-4">
                            <h6 class="mb-3">Oportunidades de Upsell</h6>
                            <ul class="recommendations-list upsell-list"></ul>
                        </div>
                        <div class="col-md-4">
                            <h6 class="mb-3">Oportunidades de Cross-sell</h6>
                            <ul class="recommendations-list crosssell-list"></ul>
                        </div>
                    </div>
                </div>
            `;
            resultsSection.after(recommendationsContainer);
        }
        
        // Update retention recommendations
        const retentionList = document.querySelector('.retention-list');
        retentionList.innerHTML = '';
        insights.retention_recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            retentionList.appendChild(li);
        });
        
        // Update upsell recommendations
        const upsellList = document.querySelector('.upsell-list');
        upsellList.innerHTML = '';
        insights.upsell_recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            upsellList.appendChild(li);
        });
        
        // Update cross-sell recommendations
        const crosssellList = document.querySelector('.crosssell-list');
        crosssellList.innerHTML = '';
        insights.crosssell_recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            crosssellList.appendChild(li);
        });
    }
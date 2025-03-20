// Script para gerenciar a análise RFM

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const segmentSelect = document.getElementById('segment-select');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-upload');
    const selectedFile = document.getElementById('selected-file');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadStatus = document.getElementById('upload-status');
    
    // Elementos para visualização e mapeamento
    const dataTable = document.querySelector('.table');
    const dataTableHead = dataTable.querySelector('thead tr');
    const dataTableBody = dataTable.querySelector('tbody');
    const totalRecordsInfo = document.querySelector('.text-muted.small.text-end');
    
    // Elementos de mapeamento
    const userIdSelect = document.getElementById('user_id');
    const activityDateSelect = document.getElementById('activity_date');
    const frequencySelect = document.getElementById('frequency');
    const consumptionTimeSelect = document.getElementById('consumption_time');
    
    // Variáveis para armazenar dados
    let csvFile = null;
    let csvData = null;
    let csvHeaders = [];
    let selectedSegment = '';
    
    // Definição dos campos por segmento
    const segmentFields = {
        'ecommerce': {
            'user_id': 'ID do Cliente',
            'activity_date': 'Data da Última Compra (Recência)',
            'frequency': 'Número Total de Compras (Frequência)',
            'consumption_time': 'Valor Total Gasto (Valor Monetário)'
        },
        'assinatura_de_varejo': {
            'user_id': 'ID do Cliente',
            'activity_date': 'Data da Última Compra (Recência)',
            'frequency': 'Número Total de Compras (Frequência)',
            'consumption_time': 'Valor Total Gasto (Valor Monetário)'
        },
        'seguros_plano_de_saude': {
            'user_id': 'ID do Cliente',
            'activity_date': 'Data da Última Utilização do Plano (Recência)',
            'frequency': 'Número Total de Utilizações do Plano (Frequência)',
            'consumption_time': 'Valor Total Pago no Plano (Valor Monetário)'
        },
        'educacao_cursos_online': {
            'user_id': 'ID do Cliente',
            'activity_date': 'Data do Último Curso Matriculado ou Acessado (Recência)',
            'frequency': 'Número Total de Cursos Matriculados (Frequência)',
            'consumption_time': 'Valor Total Gasto em Cursos (Valor Monetário)'
        },
        'telecomunicacao_provedores_de_internet': {
            'user_id': 'ID do Cliente',
            'activity_date': 'Data do Último Pagamento ou Uso do Serviço (Recência)',
            'frequency': 'Número Total de Pagamentos Mensais (Frequência)',
            'consumption_time': 'Valor Total Pago pelo Cliente (Valor Monetário)'
        },
        'agencia_de_turismo-hotelaria': {
            'user_id': 'ID do Cliente (ou CPF, e-mail)',
            'activity_date': 'Data da Última Reserva/Hospedagem (Recência)',
            'frequency': 'Número Total de Reservas (Frequência)',
            'consumption_time': 'Valor Total Gasto em Reservas (Valor Monetário)'
        }
    };
    
    // Inicializa o estado do dropzone como desabilitado
    disableDropZone();
    
    // Evento de mudança no segmento
    segmentSelect.addEventListener('change', function() {
        selectedSegment = this.value;
        updateFieldLabels();
        validateForm();
        
        // Habilita ou desabilita o dropzone com base na seleção do segmento
        if (selectedSegment) {
            enableDropZone();
        } else {
            disableDropZone();
        }
    });
    
    // Função para desabilitar o dropzone
    function disableDropZone() {
        dropZone.classList.add('disabled');
        dropZone.style.opacity = '0.6';
        dropZone.style.cursor = 'not-allowed';
        
        // Adiciona uma mensagem de aviso
        if (!document.getElementById('segment-warning')) {
            const warningMsg = document.createElement('div');
            warningMsg.id = 'segment-warning';
            warningMsg.className = 'alert alert-warning mt-2';
            warningMsg.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Selecione um segmento na Etapa 1 antes de prosseguir.';
            dropZone.parentNode.appendChild(warningMsg);
        }
    }
    
    // Função para habilitar o dropzone
    function enableDropZone() {
        dropZone.classList.remove('disabled');
        dropZone.style.opacity = '1';
        dropZone.style.cursor = 'pointer';
        
        // Remove a mensagem de aviso se existir
        const warningMsg = document.getElementById('segment-warning');
        if (warningMsg) {
            warningMsg.remove();
        }
    }
    
    // Atualiza os labels dos campos de acordo com o segmento selecionado
    function updateFieldLabels() {
        if (!selectedSegment || !segmentFields[selectedSegment]) return;
        
        const fields = segmentFields[selectedSegment];
        
        document.querySelector('label[for="user_id"]').textContent = fields.user_id + ' ';
        document.querySelector('label[for="user_id"]').appendChild(createRequiredSpan());
        
        document.querySelector('label[for="activity_date"]').textContent = fields.activity_date + ' ';
        document.querySelector('label[for="activity_date"]').appendChild(createRequiredSpan());
        
        document.querySelector('label[for="frequency"]').textContent = fields.frequency + ' ';
        document.querySelector('label[for="frequency"]').appendChild(createRequiredSpan());
        
        document.querySelector('label[for="consumption_time"]').textContent = fields.consumption_time + ' ';
        document.querySelector('label[for="consumption_time"]').appendChild(createRequiredSpan());
    }
    
    function createRequiredSpan() {
        const span = document.createElement('span');
        span.className = 'text-danger';
        span.textContent = '*';
        return span;
    }
    
    // Previne o comportamento padrão de abrir o arquivo no navegador
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Adiciona classe de destaque quando o arquivo é arrastado sobre a área
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        // Só adiciona highlight se o dropzone estiver habilitado
        if (!dropZone.classList.contains('disabled')) {
            dropZone.classList.add('highlight');
        }
    }

    function unhighlight() {
        dropZone.classList.remove('highlight');
    }

    // Processa o arquivo quando for solto na área
    dropZone.addEventListener('drop', function(e) {
        // Só processa o drop se o dropzone estiver habilitado
        if (!dropZone.classList.contains('disabled')) {
            handleDrop(e);
        }
    }, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Processa o arquivo quando selecionado pelo input
    fileInput.addEventListener('change', function() {
        // Só processa a seleção se o dropzone estiver habilitado
        if (!dropZone.classList.contains('disabled')) {
            handleFiles(this.files);
        }
    });

    // Permite clicar na área para selecionar um arquivo
    dropZone.addEventListener('click', function() {
        // Só permite clicar se o dropzone estiver habilitado
        if (!dropZone.classList.contains('disabled')) {
            fileInput.click();
        } else {
            // Alerta o usuário para selecionar um segmento primeiro
            alert('Por favor, selecione um segmento na Etapa 1 antes de fazer upload de um arquivo.');
            // Destaca o select de segmento para chamar atenção do usuário
            segmentSelect.focus();
        }
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            
            // Verifica se é um arquivo CSV
            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                // Verifica o tamanho do arquivo (limite de 30MB)
                if (file.size <= 30 * 1024 * 1024) {
                    csvFile = file;
                    displayFileInfo(file);
                    readCSVFile(file);
                } else {
                    alert('O arquivo excede o limite de 30MB. Por favor, selecione um arquivo menor.');
                }
            } else {
                alert('Por favor, selecione um arquivo CSV válido.');
            }
        }
    }

    function displayFileInfo(file) {
        // Exibe informações do arquivo selecionado
        selectedFile.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>${file.name}</strong> (${formatFileSize(file.size)})
            </div>
        `;
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Lê o arquivo CSV e exibe os dados
    function readCSVFile(file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            let contents = e.target.result;
            
            // Detecta e remove BOM (Byte Order Mark) se presente
            if (contents.charCodeAt(0) === 0xFEFF) {
                contents = contents.slice(1);
            }
            
            parseCSV(contents);
        };
        
        reader.onerror = function() {
            alert('Erro ao ler o arquivo.');
        };
        
        // Tenta ler o arquivo como UTF-8
        reader.readAsText(file, 'UTF-8');
    }
    
    // Analisa o conteúdo CSV usando Papa Parse
    function parseCSV(content) {
        // Usa Papa Parse para analisar o CSV com configurações aprimoradas
        const parseResult = Papa.parse(content, {
            header: true,
            skipEmptyLines: 'greedy', // Ignora linhas vazias de forma mais agressiva
            trimHeaders: true,
            delimiter: "", // Auto-detecção de delimitador
            encoding: "UTF-8",
            transform: function(value) {
                // Limpa espaços em branco extras e caracteres problemáticos
                return value ? value.trim() : value;
            },
            error: function(error) {
                console.error('Erro de parsing:', error);
            }
        });
        
        // Filtra erros críticos que impedem o processamento
        const criticalErrors = parseResult.errors.filter(e => e.type !== 'FieldMismatch');
        
        if (criticalErrors.length > 0) {
            console.error('Erros ao analisar CSV:', criticalErrors);
            alert('Ocorreram erros ao analisar o arquivo CSV. Verifique se o formato está correto.');
        }
        
        if (parseResult.data.length === 0) {
            alert('O arquivo CSV está vazio ou não foi possível extrair dados.');
            return;
        }
        
        // Obtém os cabeçalhos
        const headers = parseResult.meta.fields;
        csvHeaders = headers;
        
        // Obtém os dados
        const data = parseResult.data;
        
        csvData = data;
        
        // Atualiza a visualização dos dados
        updateDataVisualization(headers, data);
        
        // Atualiza as opções de mapeamento
        updateMappingOptions(headers);
        
        // Valida o formulário
        validateForm();
    }
    
    // Atualiza a visualização dos dados na tabela
    function updateDataVisualization(headers, data) {
        // Limpa a tabela
        dataTableHead.innerHTML = '';
        dataTableBody.innerHTML = '';
        
        // Adiciona os cabeçalhos
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            dataTableHead.appendChild(th);
        });
        
        // Adiciona as linhas de dados (até 5 linhas)
        const rowsToShow = Math.min(5, data.length);
        for (let i = 0; i < rowsToShow; i++) {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = data[i][header] || '';
                tr.appendChild(td);
            });
            dataTableBody.appendChild(tr);
        }
        
        // Se não houver dados para mostrar, exibe uma mensagem
        if (data.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = headers.length;
            td.textContent = 'Nenhum dado disponível';
            td.className = 'text-center';
            tr.appendChild(td);
            dataTableBody.appendChild(tr);
        }
        
        // Atualiza as informações de registros
        totalRecordsInfo.textContent = `Total de registros: ${data.length} | Colunas detectadas: ${headers.length}`;
    }
    
    // Atualiza as opções de mapeamento
    function updateMappingOptions(headers) {
        // Limpa as opções atuais
        [userIdSelect, activityDateSelect, frequencySelect, consumptionTimeSelect].forEach(select => {
            select.innerHTML = '<option value="" selected>Selecione uma coluna</option>';
        });
        
        // Adiciona as opções de cabeçalho
        headers.forEach(header => {
            [userIdSelect, activityDateSelect, frequencySelect, consumptionTimeSelect].forEach(select => {
                const option = document.createElement('option');
                option.value = header;
                option.textContent = header;
                select.appendChild(option);
            });
        });
    }
    
    // Valida o formulário
    function validateForm() {
        const isSegmentSelected = selectedSegment !== '';
        const isFileUploaded = csvFile !== null;
        const isMappingComplete = 
            userIdSelect.value !== '' && 
            activityDateSelect.value !== '' && 
            frequencySelect.value !== '' && 
            consumptionTimeSelect.value !== '';
        
        analyzeBtn.disabled = !(isSegmentSelected && isFileUploaded && isMappingComplete);
    }
    
    // Eventos de mudança nos selects de mapeamento
    [userIdSelect, activityDateSelect, frequencySelect, consumptionTimeSelect].forEach(select => {
        select.addEventListener('change', validateForm);
    });
    
    // Inicializa o objeto de gráficos RFM
    const rfmCharts = new RFMCharts();
    
    // Evento de clique no botão de análise
    analyzeBtn.addEventListener('click', async function() {
        // Validação final
        if (!csvFile || !selectedSegment || 
            !userIdSelect.value || !activityDateSelect.value || 
            !frequencySelect.value || !consumptionTimeSelect.value) {
            alert('Por favor, preencha todos os campos obrigatórios.');
            return;
        }
        
        // Mostra o status de upload
        uploadStatus.classList.remove('d-none');
        
        try {
            // Prepara os dados para envio
            const formData = new FormData();
            formData.append('file', csvFile);
            formData.append('segment_type', selectedSegment);
            formData.append('user_id_col', userIdSelect.value);
            formData.append('recency_col', activityDateSelect.value);
            formData.append('frequency_col', frequencySelect.value);
            formData.append('monetary_col', consumptionTimeSelect.value);
            
            // Envia os dados para o servidor usando o cliente API centralizado
            const analysisResults = await apiClient.analyzeRFM(formData);
            
            // Atualiza os gráficos e estatísticas
            updateAnalysisResults(analysisResults);
            
            // Atualiza o histórico de análises
            updateAnalysisHistory();
            
            // Rola para a seção de resultados
            document.querySelector('.card-header:contains("Resultados da Análise")').closest('.card').scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Erro na análise:', error);
            alert(`Erro ao analisar dados: ${error.message}`);
        } finally {
            // Esconde o status de upload
            uploadStatus.classList.add('d-none');
        }
    });
    
    /**
     * Atualiza os resultados da análise na interface
     * @param {Object} analysisResults - Resultados da análise RFM
     */
    function updateAnalysisResults(analysisResults) {
        // Substitui os placeholders dos gráficos por canvas
        const treemapPlaceholder = document.querySelector('.card-header:contains("Matriz RFM")').nextElementSibling.querySelector('.chart-placeholder');
        treemapPlaceholder.innerHTML = '';
        treemapPlaceholder.id = 'rfm-treemap';
        
        const polarAreaPlaceholder = document.querySelector('.card-header:contains("Distribuição de Segmentos")').nextElementSibling.querySelector('.chart-placeholder');
        polarAreaPlaceholder.innerHTML = '';
        const polarAreaCanvas = document.createElement('canvas');
        polarAreaCanvas.id = 'segment-distribution';
        polarAreaPlaceholder.appendChild(polarAreaCanvas);
        
        const predictivePlaceholder = document.querySelector('.card-header:contains("Matriz de Análises Preditivas")').nextElementSibling.querySelector('.chart-placeholder');
        predictivePlaceholder.innerHTML = '';
        const predictiveCanvas = document.createElement('canvas');
        predictiveCanvas.id = 'predictive-matrix';
        predictivePlaceholder.appendChild(predictiveCanvas);
        
        // Atualiza todos os gráficos
        rfmCharts.updateAllCharts(analysisResults);
    }
    
    /**
     * Atualiza o histórico de análises
     */
    async function updateAnalysisHistory() {
        try {
            const historyData = await apiClient.getAnalysisHistory();
            const historyEntries = historyData.history || [];
            
            // Atualiza a tabela de histórico
            const historyTable = document.querySelector('.step-title:contains("Histórico de Análises")').closest('.step-block').querySelector('tbody');
            historyTable.innerHTML = '';
            
            historyEntries.forEach(entry => {
                const tr = document.createElement('tr');
                
                const fileNameTd = document.createElement('td');
                fileNameTd.textContent = entry.filename;
                tr.appendChild(fileNameTd);
                
                const dateTd = document.createElement('td');
                dateTd.textContent = new Date(entry.date).toLocaleDateString('pt-BR');
                tr.appendChild(dateTd);
                
                const segmentTd = document.createElement('td');
                segmentTd.textContent = entry.segment_type;
                tr.appendChild(segmentTd);
                
                const actionsTd = document.createElement('td');
                actionsTd.className = 'text-end';
                actionsTd.innerHTML = `
                    <button class="btn btn-sm btn-outline-primary view-analysis" data-analysis-id="${entry.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary download-analysis" data-analysis-id="${entry.id}">
                        <i class="fas fa-download"></i>
                    </button>
                `;
                tr.appendChild(actionsTd);
                
                historyTable.appendChild(tr);
            });
        } catch (error) {
            console.error('Erro ao obter histórico:', error);
        }
    }
    
    // Carrega o histórico de análises ao iniciar a página
    updateAnalysisHistory();
});
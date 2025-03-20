/**
 * RFM Insights - Marketplace Script
 * Controla a funcionalidade específica da página de marketplace
 */

window.jsPDF = window.jspdf.jsPDF;
let regenerationAttempts = 0;
const maxAttempts = 3;
let currentMessageIds = [];
let currentMessages = [];
let currentSequenceIndex = 0;

document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generateButton');
    const regenerateButton = document.getElementById('regenerateButton');
    const downloadButton = document.getElementById('downloadButton');
    const form = document.getElementById('campaignForm');
    const messagePreviewModal = new bootstrap.Modal(document.getElementById('messagePreviewModal'));
    const nextMessageButton = document.getElementById('nextMessageButton');
    const prevMessageButton = document.getElementById('prevMessageButton');
    const messageCounter = document.getElementById('messageCounter');

    // Load message history
    loadMessageHistory();

    // Initialize message navigation buttons
    if (nextMessageButton) {
        nextMessageButton.addEventListener('click', function() {
            if (currentSequenceIndex < currentMessages.length - 1) {
                currentSequenceIndex++;
                displayCurrentMessage();
            }
        });
    }

    if (prevMessageButton) {
        prevMessageButton.addEventListener('click', function() {
            if (currentSequenceIndex > 0) {
                currentSequenceIndex--;
                displayCurrentMessage();
            }
        });
    }

    generateButton.addEventListener('click', async function() {
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            generateButton.disabled = true;
            
            const result = await apiClient.generateMessage(data);
            currentMessageIds = result.ids || [];
            currentMessages = result.messages || [];
            currentSequenceIndex = 0;
            
            displayCurrentMessage();
            regenerationAttempts = 0;
            updateRegenerateButton();
            downloadButton.disabled = false;
            loadMessageHistory();
        } catch (error) {
            alert('Erro ao gerar mensagem: ' + error.message);
        } finally {
            generateButton.disabled = false;
        }
    });

    regenerateButton.addEventListener('click', async function() {
        if (regenerationAttempts >= maxAttempts) {
            alert('Limite de regenerações atingido');
            return;
        }

        try {
            regenerateButton.disabled = true;
            
            const result = await apiClient.regenerateMessage(currentMessageIds[currentSequenceIndex]);
            currentMessageIds[currentSequenceIndex] = result.id;
            currentMessages[currentSequenceIndex] = result.message;
            
            displayCurrentMessage();
            regenerationAttempts++;
            updateRegenerateButton();
            loadMessageHistory();
        } catch (error) {
            alert('Erro ao regenerar mensagem: ' + error.message);
        } finally {
            regenerateButton.disabled = false;
        }
    });

    downloadButton.addEventListener('click', async function() {
        try {
            // Mock PDF generation for mockup environment
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Get the current message content
            const content = document.getElementById('generatedText').innerText;
            const messageId = currentMessageIds[currentSequenceIndex];
            
            // Add content to PDF
            doc.setFontSize(16);
            doc.text(`RFM Insights - Mensagem ${currentSequenceIndex + 1} de ${currentMessages.length}`, 20, 20);
            doc.setFontSize(12);
            
            // Split text to fit on page
            const splitText = doc.splitTextToSize(content, 170);
            doc.text(splitText, 20, 30);
            
            // Save the PDF
            doc.save(`mensagem-${messageId}.pdf`);
            
            alert('PDF gerado com sucesso!');
        } catch (error) {
            console.error('Erro ao gerar PDF:', error);
            alert('Erro ao gerar PDF. Verifique se a biblioteca jsPDF está carregada corretamente.');
        }
    });

    // Preview message from history
    document.getElementById('historyTableBody').addEventListener('click', async function(event) {
        if (event.target.classList.contains('fa-eye')) {
            const messageId = event.target.closest('button').dataset.messageId;
            try {
                // Mock preview for mockup environment
                let previewMessage = '';
                
                // Generate a preview message based on the message ID
                if (currentMessageIds.includes(messageId)) {
                    // If it's one of the current messages, use the content from currentMessages
                    const index = currentMessageIds.indexOf(messageId);
                    previewMessage = currentMessages[index] || '';
                } else {
                    // Otherwise, generate a mock message based on the ID
                    const messageType = messageId.includes('123456789') ? 'email' : 
                                       messageId.includes('987654321') ? 'whatsapp' : 'sms';
                    const segment = messageId.includes('123456789') ? 'champions' : 
                                   messageId.includes('987654321') ? 'loyal' : 'at_risk';
                    const objective = messageId.includes('123456789') ? 'retention' : 
                                     messageId.includes('987654321') ? 'upsell' : 'reactivation';
                    
                    previewMessage = `<h4>Campanha para ${segment} - ${objective}</h4>`;
                    previewMessage += `<p>Olá, somos a Empresa ABC!</p>`;
                    
                    if (messageType === 'email') {
                        previewMessage += `<p>Somos uma empresa dedicada a oferecer os melhores produtos.</p>`;
                        previewMessage += `<p>Temos uma oferta especial para você!</p>`;
                        previewMessage += `<p>Visite nossa loja e ganhe 15% de desconto na sua próxima compra!</p>`;
                        previewMessage += `<p>Acesse: <a href="https://www.empresa.com.br">www.empresa.com.br</a></p>`;
                    } else if (messageType === 'whatsapp') {
                        previewMessage += `<p>Temos uma oferta especial para você! 🎁</p>`;
                        previewMessage += `<p>Ganhe 15% de desconto na sua próxima compra!</p>`;
                    } else { // SMS
                        previewMessage += `<p>Oferta especial: 15% de desconto na sua proxima compra! Valido ate o fim do mes.</p>`;
                    }
                }
                
                document.getElementById('previewText').innerHTML = previewMessage;
                messagePreviewModal.show();
            } catch (error) {
                alert('Erro ao visualizar mensagem: ' + error.message);
            }
        } else if (event.target.classList.contains('fa-download')) {
            const messageId = event.target.closest('button').dataset.messageId;
            try {
                // Mock PDF generation for history items
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF();
                
                // Create mock content based on message ID
                let content = `Mensagem ID: ${messageId}\n\n`;
                content += "Conteúdo da mensagem gerada para a campanha.\n";
                content += "Esta é uma demonstração de download de PDF no ambiente de mockup.";
                
                // Add content to PDF
                doc.setFontSize(16);
                doc.text('RFM Insights - Mensagem Histórica', 20, 20);
                doc.setFontSize(12);
                
                // Split text to fit on page
                const splitText = doc.splitTextToSize(content, 170);
                doc.text(splitText, 20, 30);
                
                // Save the PDF
                doc.save(`mensagem-${messageId}.pdf`);
                
                alert('PDF histórico gerado com sucesso!');
            } catch (error) {
                console.error('Erro ao gerar PDF:', error);
                alert('Erro ao gerar PDF. Verifique se a biblioteca jsPDF está carregada corretamente.');
            }
        }
    });

    // Function to display the current message in the sequence
    function displayCurrentMessage() {
        if (currentMessages.length > 0 && currentSequenceIndex >= 0 && currentSequenceIndex < currentMessages.length) {
            displayGeneratedText(currentMessages[currentSequenceIndex]);
            updateMessageCounter();
            updateNavigationButtons();
        }
    }

    // Update message counter display
    function updateMessageCounter() {
        if (messageCounter && currentMessages.length > 0) {
            messageCounter.textContent = `${currentSequenceIndex + 1} de ${currentMessages.length}`;
        }
    }

    // Update navigation buttons state
    function updateNavigationButtons() {
        if (prevMessageButton) {
            prevMessageButton.disabled = currentSequenceIndex <= 0;
        }
        if (nextMessageButton) {
            nextMessageButton.disabled = currentSequenceIndex >= currentMessages.length - 1;
        }
    }
});

// Display generated text
function displayGeneratedText(message) {
    document.getElementById('generatedText').innerHTML = message;
}

// Update regenerate button state
function updateRegenerateButton() {
    const button = document.getElementById('regenerateButton');
    button.textContent = `Regenerar (${regenerationAttempts}/${maxAttempts})`;
    button.disabled = regenerationAttempts >= maxAttempts;
}

// Load message history
async function loadMessageHistory() {
    try {
        // Get message history from API
        const result = await apiClient.getUserMessages();
        const historyData = result.messages || [];
        
        const tableBody = document.getElementById('historyTableBody');
        tableBody.innerHTML = '';
        
        historyData.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(item.created_at).toLocaleDateString('pt-BR')}</td>
                <td>${formatMessageType(item.message_type)}</td>
                <td>${formatSegment(item.segment)}</td>
                <td>${formatObjective(item.objective)}</td>
                <td>${formatSeasonality(item.seasonality)}</td>
                <td>
                    <span class="badge bg-info">${item.sequence_number}/${item.sequence_total}</span>
                    <button class="btn btn-sm btn-outline-primary" data-message-id="${item.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" data-message-id="${item.id}">
                        <i class="fas fa-download"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

// Format helper functions
function formatMessageType(type) {
    const types = {
        'sms': 'SMS',
        'whatsapp': 'WhatsApp',
        'email': 'Email'
    };
    return types[type] || type;
}

function formatSegment(segment) {
    const segments = {
        'champions': 'Champions',
        'loyal': 'Loyal Customers',
        'lost': 'Lost Customers',
        'at_risk': 'At Risk'
    };
    return segments[segment] || segment;
}

function formatObjective(objective) {
    const objectives = {
        'retention_de_clientes': 'Retenção de Clientes',
        'reativacao_de_clientes_inativos': 'Reativação de Clientes',
        'upsell': 'Upsell',
        'cross-sell': 'Cross-sell',
        'fidelizacao_de_clientes': 'Fidelização de Clientes',
        'aumento_de_ticket_medio': 'Aumento de Ticket Médio'
    };
    return objectives[objective] || objective;
}

function formatSeasonality(seasonality) {
    const seasonalities = {
        'none': 'Sem sazonalidade',
        'consumer_day': 'Dia do Consumidor',
        'easter': 'Páscoa',
        'mothers_day': 'Dia das Mães',
        'valentines_day': 'Dia dos Namorados',
        'fathers_day': 'Dia dos Pais',
        'customer_day': 'Dia do Cliente',
        'children_day': 'Dia das Crianças',
        'black_friday': 'Black Friday',
        'cyber_monday': 'Cyber Monday',
        'christmas': 'Natal',
        'back_to_school': 'Volta às Aulas',
        'store_anniversary': 'Aniversário da Loja',
        'june_party': 'Festa Junina/Julina'
    };
    return seasonalities[seasonality] || seasonality;
}
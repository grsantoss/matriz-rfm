// RFM Insights - Integração JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize modal functionality
    const jsonPayloadModal = new bootstrap.Modal(document.getElementById('jsonPayloadModal'));
    const viewJsonPayloadBtn = document.getElementById('view-json-payload');
    const addWebhookBtn = document.getElementById('add-webhook');
    const webhooksContainer = document.getElementById('webhooks-container');
    const webhooksTableBody = document.getElementById('webhooks-table-body');
    const eventHistoryTableBody = document.querySelector('.card:nth-of-type(3) tbody');
    
    // Webhook management variables
    let webhooks = [];
    const MAX_WEBHOOKS = 2;
    let editingWebhookId = null;
    
    // Event history storage
    let eventHistory = [];
    
    // Initialize with one empty webhook
    if (webhooksContainer.children.length === 0) {
        addNewWebhookForm();
    }
    
    // Initial update of button state
    updateAddWebhookButtonState();
    
    // JSON Payload Modal
    if (viewJsonPayloadBtn) {
        viewJsonPayloadBtn.addEventListener('click', function() {
            // Show the example payload from the HTML
            const modalContent = document.querySelector('#jsonPayloadModal .webhook-json');
            if (modalContent) {
                // The example payload is already in the HTML, so we don't need to modify it
                jsonPayloadModal.show();
            }
        });
    }
    
    // Add Webhook Button
    if (addWebhookBtn) {
        addWebhookBtn.addEventListener('click', function() {
            const savedWebhooksCount = webhooksTableBody.querySelectorAll('tr').length;
            const formWebhooksCount = webhooksContainer.children.length;
            
            if ((savedWebhooksCount + formWebhooksCount) < MAX_WEBHOOKS) {
                addNewWebhookForm();
                updateWebhookCounter();
                updateAddWebhookButtonState();
            } else {
                alert(`Limite máximo de ${MAX_WEBHOOKS} webhooks atingido.`);
            }
        });
    }
    
    // Function to add a new webhook form
    function addNewWebhookForm() {
        const webhookCount = webhooksContainer.children.length + 1;
        const webhookId = Date.now(); // Unique ID for the webhook
        
        const webhookItem = document.createElement('div');
        webhookItem.className = 'webhook-item mb-4';
        webhookItem.dataset.id = webhookId;
        
        webhookItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                    <h6 class="mb-0 me-2">Webhook #${webhookCount}</h6>
                    <input type="text" class="form-control form-control-sm webhook-name" style="width: 200px;" placeholder="Nome do Webhook">
                </div>
            </div>
            <div class="mb-3">
                <label for="webhook-url-${webhookId}" class="form-label">URL do Webhook</label>
                <input type="url" class="form-control webhook-url" id="webhook-url-${webhookId}" placeholder="https://sua-api.com/webhook">
            </div>
            <div class="d-flex gap-2">
                <button type="button" class="btn btn-success btn-sm save-webhook" data-webhook-id="${webhookId}">Salvar Webhook</button>
                <button type="button" class="btn btn-primary btn-sm test-webhook" data-webhook-id="${webhookId}">Testar Webhook</button>
            </div>
        `;
        
        webhooksContainer.appendChild(webhookItem);
        
        // Add event listener for the test button
        const testBtn = webhookItem.querySelector('.test-webhook');
        if (testBtn) {
            testBtn.addEventListener('click', function() {
                const webhookId = this.getAttribute('data-webhook-id');
                const webhookItem = document.querySelector(`.webhook-item[data-id="${webhookId}"]`);
                const webhookName = webhookItem.querySelector('.webhook-name').value || 'Unnamed Webhook';
                const webhookUrl = webhookItem.querySelector('.webhook-url').value;
                
                if (!webhookUrl) {
                    alert('Por favor, insira uma URL válida para o webhook.');
                    return;
                }
                
                testWebhook(webhookUrl, webhookName);
            });
        }
        
        // Add event listener for the save button
        const saveBtn = webhookItem.querySelector('.save-webhook');
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                const webhookId = this.getAttribute('data-webhook-id');
                const webhookItem = document.querySelector(`.webhook-item[data-id="${webhookId}"]`);
                const webhookName = webhookItem.querySelector('.webhook-name').value || 'Webhook sem nome';
                const webhookUrl = webhookItem.querySelector('.webhook-url').value;
                
                if (!webhookUrl) {
                    alert('Por favor, insira uma URL válida para o webhook.');
                    return;
                }
                
                saveWebhook(webhookId, webhookName, webhookUrl);
            });
        }
        
        return webhookId;
    }
    
    // Function to save webhook to the management table
    function saveWebhook(webhookId, name, url) {
        // Check if we're editing an existing webhook
        const existingRow = document.querySelector(`tr[data-webhook-id="${webhookId}"]`);
        
        if (existingRow) {
            // Update existing row
            existingRow.querySelector('.webhook-table-name').textContent = name;
            existingRow.querySelector('.webhook-table-url').textContent = url;
            
            // Clear the form if we were editing
            if (editingWebhookId === webhookId) {
                const webhookItem = document.querySelector(`.webhook-item[data-id="${webhookId}"]`);
                if (webhookItem) {
                    webhookItem.remove();
                    addNewWebhookForm();
                    updateWebhookCounter();
                    updateAddWebhookButtonState();
                    editingWebhookId = null;
                }
            }
            
            alert('Webhook atualizado com sucesso!');
            
            // Add event to history
            addEventToHistory(name, 'webhook_updated', 'Sucesso');
        } else {
            // Create new row
            const newRow = document.createElement('tr');
            newRow.dataset.webhookId = webhookId;
            
            newRow.innerHTML = `
                <td class="webhook-table-name">${name}</td>
                <td class="webhook-table-url">${url}</td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary edit-webhook" data-webhook-id="${webhookId}">Editar</button>
                        <button class="btn btn-sm btn-primary test-webhook" data-webhook-id="${webhookId}">Testar</button>
                        <button class="btn btn-sm btn-outline-danger delete-webhook" data-webhook-id="${webhookId}">Excluir</button>
                    </div>
                </td>
            `;
            
            webhooksTableBody.appendChild(newRow);
            
            // Add event listeners for edit, test and delete buttons
            const editBtn = newRow.querySelector('.edit-webhook');
            editBtn.addEventListener('click', function() {
                editWebhook(webhookId, name, url);
            });
            
            const testBtn = newRow.querySelector('.test-webhook');
            testBtn.addEventListener('click', function() {
                testWebhook(url, name);
            });
            
            const deleteBtn = newRow.querySelector('.delete-webhook');
            deleteBtn.addEventListener('click', function() {
                deleteWebhook(webhookId);
            });
            
            // Clear the form and create a new empty one
            const webhookItem = document.querySelector(`.webhook-item[data-id="${webhookId}"]`);
            if (webhookItem) {
                webhookItem.remove();
                addNewWebhookForm();
                updateWebhookCounter();
                updateAddWebhookButtonState();
            }
            
            alert('Webhook salvo com sucesso!');
            
            // Add event to history
            addEventToHistory(name, 'webhook_created', 'Sucesso');
            
            // Store webhook in the array
            webhooks.push({ id: webhookId, name, url });
        }
    }
    
    // Function to edit a webhook
    function editWebhook(webhookId, name, url) {
        // Check if we're already editing a webhook
        if (editingWebhookId) {
            // If we're editing a different webhook, cancel the current edit
            const currentEditItem = document.querySelector(`.webhook-item[data-id="${editingWebhookId}"]`);
            if (currentEditItem) {
                currentEditItem.remove();
            }
        }
        
        // Remove any empty webhook forms
        const emptyForms = Array.from(webhooksContainer.children).filter(item => {
            const nameInput = item.querySelector('.webhook-name');
            const urlInput = item.querySelector('.webhook-url');
            return !nameInput.value && !urlInput.value;
        });
        
        emptyForms.forEach(form => form.remove());
        
        // Create a new form for editing
        const newWebhookId = addNewWebhookForm();
        const newWebhookItem = document.querySelector(`.webhook-item[data-id="${newWebhookId}"]`);
        
        // Set the form values
        const nameInput = newWebhookItem.querySelector('.webhook-name');
        const urlInput = newWebhookItem.querySelector('.webhook-url');
        nameInput.value = name;
        urlInput.value = url;
        
        // Mark this as the webhook being edited
        newWebhookItem.dataset.originalId = webhookId;
        editingWebhookId = webhookId;
        
        // Update the save button to indicate we're editing
        const saveBtn = newWebhookItem.querySelector('.save-webhook');
        saveBtn.textContent = 'Atualizar Webhook';
        saveBtn.classList.remove('btn-success');
        saveBtn.classList.add('btn-warning');
        
        // Update counters and button states
        updateWebhookCounter();
        updateAddWebhookButtonState();
    }
    
    // Function to delete a webhook
    function deleteWebhook(webhookId) {
        if (confirm('Tem certeza que deseja excluir este webhook?')) {
            const row = document.querySelector(`tr[data-webhook-id="${webhookId}"]`);
            if (row) {
                const webhookName = row.querySelector('.webhook-table-name').textContent;
                row.remove();
                
                // If this was the webhook being edited, clear the form
                if (editingWebhookId === webhookId) {
                    const editItem = document.querySelector(`.webhook-item[data-id="${editingWebhookId}"]`);
                    if (editItem) {
                        editItem.remove();
                        addNewWebhookForm();
                    }
                    editingWebhookId = null;
                }
                
                updateWebhookCounter();
                updateAddWebhookButtonState();
                alert('Webhook excluído com sucesso!');
                
                // Add event to history
                addEventToHistory(webhookName, 'webhook_deleted', 'Sucesso');
                
                // Remove webhook from the array
                webhooks = webhooks.filter(webhook => webhook.id !== webhookId);
            }
        }
    }
    
    // Function to update webhook counter (numbers)
    function updateWebhookCounter() {
        const webhookItems = webhooksContainer.querySelectorAll('.webhook-item');
        webhookItems.forEach((item, index) => {
            const counter = item.querySelector('h6');
            counter.textContent = `Webhook #${index + 1}`;
        });
    }
    
    // Function to update the state of the Add Webhook button
    function updateAddWebhookButtonState() {
        if (addWebhookBtn) {
            // Count saved webhooks in the table
            const savedWebhooksCount = webhooksTableBody.querySelectorAll('tr').length;
            // Count form webhooks
            const formWebhooksCount = webhooksContainer.children.length;
            
            // Disable the add button if we've reached the maximum number of webhooks
            addWebhookBtn.disabled = (savedWebhooksCount + formWebhooksCount) >= MAX_WEBHOOKS;
            
            // Hide the form container if we've reached the maximum and there are no forms
            if (savedWebhooksCount >= MAX_WEBHOOKS && formWebhooksCount === 0) {
                webhooksContainer.classList.add('d-none');
            } else {
                webhooksContainer.classList.remove('d-none');
            }
        }
    }
    
    // Function to test webhook
    async function testWebhook(url, name) {
        try {
            const testPayload = {
                event: 'webhook_test',
                timestamp: new Date().toISOString(),
                webhook_name: name || 'Unnamed Webhook',
                test: true,
                data: {
                    test_id: Math.random().toString(36).substring(7),
                    message: 'Esta é uma carga útil de teste para verificar a configuração do webhook'
                }
            };
            
            // Show test payload in modal
            const modalContent = document.querySelector('#jsonPayloadModal .webhook-json');
            if (modalContent) {
                modalContent.innerHTML = `
                    <div class="mb-3">
                        <h6>Testando Webhook: ${name}</h6>
                        <p>URL: ${url}</p>
                    </div>
                    <pre>${JSON.stringify(testPayload, null, 2)}</pre>
                    <div class="mt-3">
                        <button class="btn btn-primary send-test-payload">Enviar Payload de Teste</button>
                    </div>
                `;
                
                // Add event listener for send button
                const sendButton = modalContent.querySelector('.send-test-payload');
                if (sendButton) {
                    sendButton.addEventListener('click', async () => {
                        try {
                            // Simulate sending the webhook
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            
                            // Add test event to history
                            addEventToHistory(name, 'webhook_test', 'Sucesso', testPayload);
                            
                            alert(`Teste do webhook "${name}" realizado com sucesso!`);
                            jsonPayloadModal.hide();
                        } catch (error) {
                            // Add failed test to history
                            addEventToHistory(name, 'webhook_test', 'Erro', testPayload);
                            alert(`Erro ao testar webhook: ${error.message}`);
                        }
                    });
                }
                
                jsonPayloadModal.show();
            }
        } catch (error) {
            alert(`Erro ao testar webhook: ${error.message}`);
        }
    }
    
    // Function to add event to history
    function addEventToHistory(webhookName, eventType, status, payload = null) {
        const now = new Date();
        const event = {
            timestamp: now.toISOString(),
            webhookName,
            eventType,
            status,
            payload
        };
        
        // Add to event history array
        eventHistory.unshift(event);
        
        // Create table row
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${now.toLocaleString()}</td>
            <td>${webhookName}</td>
            <td>${eventType.replace('webhook_', '').replace('_', ' ')}</td>
            <td><span class="badge ${status === 'Sucesso' ? 'bg-success' : 'bg-danger'}">${status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-secondary view-payload" data-event-id="${eventHistory.length - 1}">
                    Ver Payload
                </button>
            </td>
        `;
        
        // Add click handler for payload button
        const payloadBtn = row.querySelector('.view-payload');
        payloadBtn.addEventListener('click', () => {
            const eventId = parseInt(payloadBtn.getAttribute('data-event-id'));
            const event = eventHistory[eventId];
            
            if (event && event.payload) {
                const modalContent = document.querySelector('#jsonPayloadModal .webhook-json');
                if (modalContent) {
                    modalContent.innerHTML = `
                        <div class="mb-3">
                            <h6>Payload do Evento</h6>
                            <p>Webhook: ${event.webhookName}</p>
                            <p>Evento: ${event.eventType}</p>
                            <p>Status: ${event.status}</p>
                            <p>Data/Hora: ${new Date(event.timestamp).toLocaleString()}</p>
                        </div>
                        <pre>${JSON.stringify(event.payload, null, 2)}</pre>
                    `;
                    jsonPayloadModal.show();
                }
            }
        });
        
        // Add to table
        if (eventHistoryTableBody) {
            // Keep only the last 30 days of events
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            
            // Remove old events from DOM
            while (eventHistoryTableBody.children.length > 50) {
                eventHistoryTableBody.lastChild.remove();
            }
            
            // Add new event at the top
            eventHistoryTableBody.insertBefore(row, eventHistoryTableBody.firstChild);
        }
    }
});
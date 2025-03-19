// Script para gerenciar o upload de arquivos CSV via drag and drop

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-upload');
    const selectedFile = document.getElementById('selected-file');

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
        dropZone.classList.add('highlight');
    }

    function unhighlight() {
        dropZone.classList.remove('highlight');
    }

    // Processa o arquivo quando for solto na área
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Processa o arquivo quando selecionado pelo input
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    // Permite clicar na área para selecionar um arquivo
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            // Verifica se é um arquivo CSV
            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                displayFileInfo(file);
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
});
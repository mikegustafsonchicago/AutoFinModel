//=============================================================
//                     1. CONFIGURATION & CONSTANTS
//=============================================================
import { clearAllData, uploadFile, dollarFormatter } from './shared-modules.js';

let project_name;
let project_type;
let USER_NAME;
let APP_STATE = {
    initialized: false,
    loading: true,
    error: null
};

// Store dynamically created tables here
const AppTables = {};

//=============================================================
//                     2. INITIALIZATION
//=============================================================

async function initializeApp() {
    try {
        toggleLoading(true);
        
        const response = await fetch('/api/init');
        if (!response.ok) throw new Error('Failed to get initialization data');
        const initData = await response.json();
        
        USER_NAME = initData.user.username;
        project_name = initData.project.currentProject;
        project_type = initData.project.projectType;
        
        if (initData.system.hasExistingFiles) {
            await initializeExistingSession(initData);
        } else {
            await initializeNewSession(initData);
        }
        
        APP_STATE.initialized = true;
    } catch (error) {
        console.error('Initialization failed:', error);
        APP_STATE.error = error.message;
        showErrorMessage('Failed to initialize application. Please refresh the page or contact support.');
    } finally {
        APP_STATE.loading = false;
        toggleLoading(false);
    }
}

async function initializeExistingSession(initData) {
    initializeModals();
    initializeLoadProjectButton();
    initializeUploadZone();
    initializeAddRowButtons();
    initializeAIButtons();
    bindStaticEventHandlers();
    
    await updateProjectsDropdown(initData.project.availableProjects);
    updateProjectUI(initData.project.currentProject);
    
    // If you want to load dynamic tables after initialization, do it here
    initializeDynamicTables();
}

async function initializeNewSession(initData) {
    initializeModals();
    showNewProjectModal();
    initializeLoadProjectButton();
    bindStaticEventHandlers();
}

// Update current project UI
function updateProjectUI(projectName) {
    const projectHeader = document.getElementById('currentProjectHeader');
    if (projectHeader) {
        projectHeader.textContent = projectName || 'No Project Selected';
    }
}

async function updateProjectsDropdown(projects) {
    const dropdown = document.getElementById('existingProjects');
    if (!dropdown) return;
    dropdown.innerHTML = '';
    
    projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project;
        option.textContent = project;
        dropdown.appendChild(option);
    });
}

function showErrorMessage(message) {
    const errorContainer = document.getElementById('errorContainer') || createErrorContainer();
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
}

function createErrorContainer() {
    const container = document.createElement('div');
    container.id = 'errorContainer';
    container.className = 'alert alert-danger';
    document.body.insertBefore(container, document.body.firstChild);
    return container;
}

//=============================================================
//                     3. DOM LOADED EVENT
//=============================================================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp().catch(error => {
        console.error('Failed to initialize application:', error);
        showErrorMessage('Application initialization failed. Please refresh the page.');
    });
});

//=============================================================
//                     4. MODAL & PROJECT CONTROL
//=============================================================
function initializeModals() {
    const newProjectModal = document.getElementById('newProjectModal');
    if (newProjectModal) {
        newProjectModal.addEventListener('show.bs.modal', () => {});
    }

    const createProjectBtn = document.querySelector('#newProjectModal .btn-primary');
    if (createProjectBtn) {
        createProjectBtn.addEventListener('click', createNewProject);
    }
}

function initializeLoadProjectButton() {
    const loadProjectBtn = document.getElementById('loadProjectButton');
    if (loadProjectBtn) {
        loadProjectBtn.addEventListener('click', loadProject);
    }
}

function showNewProjectModal() {
    const modal = new bootstrap.Modal(document.getElementById('newProjectModal'));
    modal.show();
}

//=============================================================
//                     5. UPLOAD ZONE SETUP
//=============================================================
function initializeUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const pdfInput = document.getElementById('pdfUpload');

    if (!uploadZone || !pdfInput) {
        console.error("initializeUploadZone: Upload elements not found");
        return;
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'));
    });

    uploadZone.addEventListener('drop', handleDropFiles);
    uploadZone.addEventListener('click', () => pdfInput.click());
    pdfInput.addEventListener('change', handleFiles);
}

function handleDropFiles(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files: files } });
}

function handleFiles(event) {
    const files = event.target.files;
    const tableBody = document.getElementById('uploadedDocsTable').querySelector('tbody');

    Array.from(files).forEach(file => {
        if (file.type === "application/pdf") {
            const row = document.createElement('tr');
            row.dataset.file = file;

            const fileNameCell = document.createElement('td');
            fileNameCell.textContent = file.name;
            row.appendChild(fileNameCell);

            const uploadCell = document.createElement('td');
            const uploadButton = document.createElement('button');
            uploadButton.innerHTML = '<span style="font-family: Arial, sans-serif;">&#x2728;</span>';
            uploadButton.onclick = () => sendFileToAI(file, row);
            uploadCell.appendChild(uploadButton);
            row.appendChild(uploadCell);

            const checkCell = document.createElement('td');
            checkCell.classList.add("check-cell");
            row.appendChild(checkCell);

            const removeCell = document.createElement('td');
            const removeButton = document.createElement('button');
            removeButton.textContent = 'X';
            removeButton.onclick = () => row.remove();
            removeCell.appendChild(removeButton);
            row.appendChild(removeCell);

            tableBody.appendChild(row);

            uploadFile(file, project_name, project_type);
        }
    });
}

//=============================================================
//                     6. BUTTON & EVENT INITIALIZATIONS
//=============================================================
function initializeAddRowButtons() {
    document.querySelectorAll('.button-outline').forEach(button => {
        button.addEventListener('click', (e) => {
            const card = e.target.closest('.card');
            const tableContainer = card.querySelector('.table-container');
            if (!tableContainer) return;

            const tableId = tableContainer.querySelector('.tabulator').id;
            const table = Tabulator.findTable(`#${tableId}`)[0];
            if (table) addRow(table);
        });
    });
}

function initializeAIButtons() {
    const pdfAIButton = document.getElementById('pdfAIButton');
    if (pdfAIButton) {
        pdfAIButton.addEventListener('click', () => preparePayload('all'));
    }
    // Add more if needed for dynamic tables
}

function bindStaticEventHandlers() {
    const clearDataButton = document.getElementById('clearDataButton');
    if (clearDataButton) {
        clearDataButton.addEventListener('click', () => {
            clearAllData(project_name, project_type);
        });
    }

    const downloadExcelButton = document.getElementById('downloadExcelButton');
    if (downloadExcelButton) {
        downloadExcelButton.addEventListener('click', downloadExcel);
    }

    const downloadPPTButton = document.getElementById('downloadPPTButton');
    if (downloadPPTButton) {
        downloadPPTButton.addEventListener('click', downloadPPT);
    }
}

//=============================================================
//                     7. DATA MANAGEMENT
//=============================================================
function preparePayload(updateScope) {
    const payload = {
        updateScope: updateScope, 
        project_type: project_type,
        project_name: project_name,
        businessDescription: document.getElementById("businessDescription").value,
        userPrompt: document.getElementById("chatgptPrompt").value,
        pdfFileName: updateScope === 'all' ? document.getElementById('uploadedPDFName').value : null
    };
    sendTextToAI(payload);
}

function addRow(table) {
    // For dynamic tables, define a default newRow structure or prompt user input
    const newRow = {}; // empty row
    table.addRow(newRow).then(() => table.redraw());
}

function adjustTableHeight(table) {
    const rowCount = table.getDataCount("active");
    const rowHeight = 35;
    const headerHeight = 40;
    const maxHeight = 600;
    const newHeight = Math.min(rowCount * rowHeight + headerHeight, maxHeight);
    table.element.style.height = `${newHeight}px`;
    table.redraw();
}

//=============================================================
//                     8. UTILITIES & API
//=============================================================
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function populateProjectsDropdown() {
    const dropdown = document.getElementById('existingProjects');
    fetch('/api/context')
        .then(response => response.json())
        .then(contextData => {
            dropdown.innerHTML = '';
            contextData.available_projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project;
                option.textContent = project;
                dropdown.appendChild(option);
            });
        })
        .catch(error => console.error('populateProjectsDropdown: Error loading context:', error));
}

function sendFileToAI(file, row) {
    console.log(`Processing ${file.name} with AI...`);
    toggleLoading(true);

    const payload = {
        fileName: file.name,
        projectName: project_name,
        projectType: project_type,
        userPrompt: document.getElementById("chatgptPrompt").value,
        updateScope: 'all'
    };

    fetch('/api/openai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        toggleLoading(false);
        if (data.error) {
            alert(`Error processing ${file.name}: ${data.error}`);
            return;
        }
        document.getElementById("aiResponse").innerHTML = `<p>AI Response Text: ${data.text}</p>`;
        row.querySelector('.check-cell').innerHTML = '&#10004;';
        // Refresh tables if needed
    })
    .catch(error => {
        toggleLoading(false);
        console.error(`sendFileToAI: Error processing ${file.name}:`, error);
    });
}

function sendTextToAI(payload) {
    toggleLoading(true);
    const aiResponseDiv = document.getElementById("aiResponse");
    aiResponseDiv.innerHTML = "";

    payload.projectName = project_name;
    payload.projectType = project_type;

    fetch('/api/openai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        toggleLoading(false);
        aiResponseDiv.innerHTML = `<p>AI Response Text: ${data.text}</p>`;
        // Refresh tables if needed
    })
    .catch(error => {
        toggleLoading(false);
        aiResponseDiv.innerHTML = `<p>Error occurred: ${error.message}</p>`;
        console.error('sendTextToAI: Error:', error);
    });
}

function toggleLoading(show) {
    const loadingIcon = document.getElementById("loading");
    if (!loadingIcon) return;
    loadingIcon.style.display = show ? "block" : "none";
}

//=============================================================
//                     9. PROJECT MANAGEMENT
//=============================================================
function loadProject() {
    const projectSelect = document.getElementById('existingProjects');
    const selectedProject = projectSelect.value;
    const projectTypeSelect = document.getElementById('projectType');
    const selectedProjectType = projectTypeSelect.value;

    if (!selectedProject) {
        alert('Please select a project');
        return;
    }

    fetch('/api/projects/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            projectName: selectedProject,
            projectType: selectedProjectType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        project_name = selectedProject;
        project_type = selectedProjectType;
        updateProjectUI(selectedProject);

        // Close modal if open
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadProjectModal'));
        if (modal) modal.hide();

        alert('Project loaded successfully!');
    })
    .catch(error => {
        console.error('loadProject: Error:', error);
        alert('Error loading project');
    });
}

function createNewProject() {
    const projectName = document.getElementById('newProjectName').value;
    const projectType = document.getElementById('projectType').value;
    if (!projectName) {
        alert('Please enter a project name');
        return;
    }

    fetch('/api/projects/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectName, projectType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        project_name = projectName;
        project_type = projectType;
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('newProjectModal'));
        if (modal) modal.hide();
        
        updateProjectUI(projectName);
        populateProjectsDropdown();
    })
    .catch(error => {
        console.error('createNewProject: Error:', error);
        alert('Error creating project');
    });
}

//=============================================================
//                     10. FILE DOWNLOADS
//=============================================================
function downloadExcel() {
    fetch(`/download_excel?project_type=${project_type}`, { method: 'GET' })
        .then(response => handleFileDownload(response, 'model.xlsx'))
        .catch(error => console.error('downloadExcel: Error:', error));
}

function downloadPPT() {
    fetch(`/download_ppt?project_type=${project_type}`, { method: 'GET' })
        .then(response => handleFileDownload(response, 'presentation.pptx'))
        .catch(error => console.error('downloadPPT: Error:', error));
}

function handleFileDownload(response, defaultFilename) {
    if (!response.ok) throw new Error(`Error downloading file: ${response.statusText}`);

    const filename = response.headers.get('Content-Disposition')
        ?.split(';')
        ?.find(n => n.includes('filename='))
        ?.replace('filename=', '')
        ?.trim() || defaultFilename;

    return Promise.all([response.blob(), Promise.resolve(filename)]).then(([blob, filename]) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    });
}

//=============================================================
//                     11. DYNAMIC TABLES
//=============================================================
function initializeDynamicTables() {
    // First get context to get list of available tables
    fetch('/api/context')
        .then(response => response.json())
        .then(context => {
            // Get list of available tables from context
            const availableTables = context.available_tables;
            
            // For each table structure file
            availableTables.forEach(tableFile => {
                // Extract table name from filename (remove _structure.json)
                const tableName = tableFile.replace('_structure.json', '');
                
                // Fetch schema for this table
                console.log(`Fetching schema for table: ${tableName}`);
                fetch(`/api/schema/${tableName}`)
                    .then(response => {
                        console.log(`Schema response for ${tableName}:`, response);
                        return response.json();
                    })
                    .then(structure => {
                        console.log(`Parsed schema structure for ${tableName}:`, structure);
                        
                        // Generate columns from structure
                        const columns = generateColumnsFromStructure(structure);
                        console.log(`Generated columns for ${tableName}:`, columns);
                        
                        // Create container ID and table ID
                        const containerId = `${tableName}TableContainer`;
                        const tableId = `${tableName}Table`;
                        
                        // Create title from table name
                        const title = tableName.charAt(0).toUpperCase() + 
                                    tableName.slice(1).replace(/_/g, ' ') + 
                                    ' Data';
                        
                        console.log(`Creating table with ID ${tableId} and title "${title}"`);
                        
                        // Create table dynamically
                        createDynamicTable(
                            containerId,
                            tableId,
                            columns,
                            [], // Initial empty data
                            title
                        );
                        
                        // Load data after table is created
                        loadDynamicTableData(tableName, AppTables[tableId]);
                    })
                    .catch(error => console.error(`Error loading ${tableName} structure:`, error));
            });
        })
        .catch(error => console.error('Error loading context:', error));
}

function loadDynamicTableData(tableIdentifier, table) {
    fetch(`/api/table_data/${tableIdentifier}`)
        .then(response => response.json())
        .then(responseData => {
            let tableData = responseData.data || [];
            if (!Array.isArray(tableData)) tableData = [tableData];
            table.setData(tableData).then(() => adjustTableHeight(table));
        })
        .catch(error => console.error(`loadDynamicTableData: Error loading ${tableIdentifier}:`, error));
}

function generateColumnsFromStructure(structure) {
    // This function will parse the structure and convert it into Tabulator column definitions
    // For example, if structure looks like the one you provided in the snippet:
    // structure.structure.revenue_sources.items.properties has the columns info
    const columns = [];

    const rootKey = Object.keys(structure.structure)[0]; // e.g. "revenue_sources"
    const properties = structure.structure[rootKey].items.properties;

    // properties is an object: { "revenue_source_name": {type:..., order:..., ...}, ... }
    // Sort by 'order' if needed
    const sortedProps = Object.entries(properties).sort((a, b) => (a[1].order || 999) - (b[1].order || 999));

    for (const [fieldName, fieldDef] of sortedProps) {
        columns.push({
            title: fieldDef.description || fieldName,
            field: fieldName,
            editor: fieldDef.type === 'number' ? "number" : "input",
            formatter: fieldName.toLowerCase().includes('price') || fieldName.toLowerCase().includes('value') ? dollarFormatter : undefined
        });
    }

    // Add delete column as last column
    columns.push({
        title: "",
        formatter: () => "<button class='delete-btn'>✖</button>",
        width: 80,
        hozAlign: "center",
        cellClick: (e, cell) => {
            cell.getRow().delete();
            cell.getTable().redraw();
        }
    });

    return columns;
}

function createDynamicTable(containerId, tableId, columns, data = [], title) {
    if (AppTables[tableId]) {
        console.warn(`Table ${tableId} already exists`);
        return AppTables[tableId];
    }

    let container = document.getElementById(containerId);
    if (!container) {
        container = document.createElement('div');
        container.id = containerId;
        container.className = 'card mb-4';

        let mainContent = document.getElementById('mainContent');
        if (!mainContent) {
            mainContent = document.createElement('div');
            mainContent.id = 'mainContent';
            document.body.appendChild(mainContent);
        }
        mainContent.appendChild(container);
    }

    container.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">${title}</h5>
            <div>
                <button class="btn btn-outline-primary btn-sm add-row-btn">Add Row</button>
                <button class="btn btn-outline-secondary btn-sm ai-btn">
                    <span style="font-family: Arial, sans-serif;">✨</span> AI
                </button>
            </div>
        </div>
        <div class="card-body">
            <div class="table-container">
                <div id="${tableId}" class="tabulator"></div>
            </div>
        </div>
    `;

    const table = new Tabulator(`#${tableId}`, {
        layout: "fitData",
        autoResize: true,
        columns: columns,
        data: data
    });

    container.querySelector('.add-row-btn').addEventListener('click', () => addRow(table));
    container.querySelector('.ai-btn').addEventListener('click', () => preparePayload(tableId));

    AppTables[tableId] = table;
    return table;
}

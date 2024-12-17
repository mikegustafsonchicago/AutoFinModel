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


const AppTables = {
    comparablesTable: null,
    revenueTable: null,
    employeesTable: null,
    historicalISTable: null,
    purchasesTable: null,
    capexTable: null,
    opexTable: null
};

//=============================================================
//                     2. INITIALIZATION
//=============================================================

async function initializeApp() {
    try {
        // Show loading state
        toggleLoading(true);
        
        // Fetch initialization data
        const response = await fetch('/api/init');
        if (!response.ok) throw new Error('Failed to get initialization data');
        const initData = await response.json();
        
        // Set global variables
        USER_NAME = initData.user.username;
        project_name = initData.project.currentProject;
        project_type = initData.project.projectType;
        
        // Initialize UI based on state
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
    // Initialize all components
    initializeModals();
    initializeLoadProjectButton();
    initializeUploadZone();
    initializeAddRowButtons();
    initializeAIButtons();
    initializeTables();
    bindStaticEventHandlers();
    
    // Update project dropdown with available projects
    await updateProjectsDropdown(initData.project.availableProjects);
    
    // Refresh tables with existing data
    await refreshTables();
    
    // Update UI to reflect current project
    updateProjectUI(initData.project.currentProject);
}

async function initializeNewSession(initData) {
    // Show new project modal by default
    initializeModals();
    showNewProjectModal();
    
    // Initialize minimal UI components
    initializeLoadProjectButton();
    bindStaticEventHandlers();
}

function updateProjectUI(projectName) {
    // Update any UI elements that show the current project
    const projectDisplay = document.getElementById('currentProject');
    if (projectDisplay) {
        projectDisplay.textContent = projectName || 'No Project Selected';
    }
}

async function updateProjectsDropdown(projects) {
    const dropdown = document.getElementById('existingProjects');
    if (!dropdown) return;
    
    // Clear existing options
    dropdown.innerHTML = '';
    
    // Add projects to dropdown
    projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project;
        option.textContent = project;
        dropdown.appendChild(option);
    });
}

function showErrorMessage(message) {
    // Add error message to the UI
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

// Update the DOMContentLoaded listener
document.addEventListener('DOMContentLoaded', () => {
    initializeApp().catch(error => {
        console.error('Failed to initialize application:', error);
        showErrorMessage('Application initialization failed. Please refresh the page.');
    });
});

document.addEventListener('DOMContentLoaded', () => {
    initializeModals();
    initializeLoadProjectButton();
    initializeUploadZone();
    initializeAddRowButtons();
    initializeAIButtons();
    initializeTables();
    bindStaticEventHandlers();
    refreshTables();
    populateProjectsDropdown(); // Populate dropdown on page load
    
});


//=============================================================
//                     3. PROJECT SELECTOR SETUP
//=============================================================

function initializeModals() {
    // Show new project modal button
    const newProjectBtn = document.querySelector('[data-bs-target="#newProjectModal"]');
    if (newProjectBtn) {
    }

    const newProjectModal = document.getElementById('newProjectModal');
    if (newProjectModal) {
        newProjectModal.addEventListener('show.bs.modal', () => {
        });
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
//                     4. UPLOAD ZONE SETUP
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
            // Add row to the uploaded docs table
            const row = document.createElement('tr');
            row.dataset.file = file;

            // File Name Cell
            const fileNameCell = document.createElement('td');
            fileNameCell.textContent = file.name;
            row.appendChild(fileNameCell);

            // Upload to AI Cell
            const uploadCell = document.createElement('td');
            const uploadButton = document.createElement('button');
            uploadButton.innerHTML = '<span style="font-family: Arial, sans-serif;">&#x2728;</span>';
            uploadButton.onclick = () => sendFileToAI(file, row);
            uploadCell.appendChild(uploadButton);
            row.appendChild(uploadCell);

            // Check Cell
            const checkCell = document.createElement('td');
            checkCell.classList.add("check-cell");
            row.appendChild(checkCell);

            // Remove Cell
            const removeCell = document.createElement('td');
            const removeButton = document.createElement('button');
            removeButton.textContent = 'X';
            removeButton.onclick = () => row.remove();
            removeCell.appendChild(removeButton);
            row.appendChild(removeCell);

            tableBody.appendChild(row);

            // Upload the file to the server
            uploadFile(file, project_name, project_type);
        }
    });
}

//=============================================================
//                     5. BUTTON & EVENT INITIALIZATIONS
//=============================================================

function initializeAddRowButtons() {
    document.querySelectorAll('.button-outline').forEach(button => {
        button.addEventListener('click', (e) => {
            const card = e.target.closest('.card');
            const tableContainer = card.querySelector('.table-container');
            if (!tableContainer) return;

            const tableId = tableContainer.id;
            const table = Tabulator.findTable(`#${tableId}`)[0];
            if (table) addRow(table);
        });
    });
}

function initializeAIButtons() {
    // PDF AI Button
    const pdfAIButton = document.getElementById('pdfAIButton');
    if (pdfAIButton) {
        pdfAIButton.addEventListener('click', () => preparePayload('all'));
    }

    // Specific table AI Buttons
    addAIButtonEvent('capexAIButton', 'capexTable');
    addAIButtonEvent('opexAIButton', 'opexTable');
    addAIButtonEvent('revenueAIButton', 'revenueTable');
    addAIButtonEvent('purchasesAIButton', 'purchasesTable');
    addAIButtonEvent('historicalISAIButton', 'historicalISTable');
}

function addAIButtonEvent(buttonId, scope) {
    const btn = document.getElementById(buttonId);
    if (btn) {
        btn.addEventListener('click', () => preparePayload(scope));
    }
}

function bindStaticEventHandlers() {
    // Clear Data
    const clearDataButton = document.getElementById('clearDataButton');
    if (clearDataButton) {
        clearDataButton.addEventListener('click', () => {
            clearAllData(project_name, project_type);
        });
    }

    // Download Excel
    const downloadExcelButton = document.getElementById('downloadExcelButton');
    if (downloadExcelButton) {
        downloadExcelButton.addEventListener('click', downloadExcel);
    }

    // Download PPT
    const downloadPPTButton = document.getElementById('downloadPPTButton');
    if (downloadPPTButton) {
        downloadPPTButton.addEventListener('click', downloadPPT);
    }
}

//=============================================================
//                     6. TABLE INITIALIZATION
//=============================================================

function initializeTables() {
    // Revenue Table
    AppTables.revenueTable = new Tabulator("#revenueTable", {
        layout: "fitData",
        autoResize: true,
        columns: getRevenueTableColumns()
    });

    // Purchases Table
    AppTables.purchasesTable = new Tabulator("#purchasesTable", {
        layout: "fitData",
        autoResize: true,
        columns: getPurchasesTableColumns()
    });

    // Employees Table
    AppTables.employeesTable = new Tabulator("#employeesTable", {
        layout: "fitData",
        columns: getEmployeesTableColumns()
    });

    // CAPEX Table
    AppTables.capexTable = new Tabulator("#capexTable", {
        layout: "fitData",
        columns: getCapexTableColumns()
    });

    // OPEX Table
    AppTables.opexTable = new Tabulator("#opexTable", {
        layout: "fitData",
        columns: getOpexTableColumns()
    });

    // Historical IS Table
    AppTables.historicalISTable = new Tabulator("#historicalISTable", {
        layout: "fitData",
        columns: getHistoricalISTableColumns()
    });

    // Comparables Table
    AppTables.comparablesTable = new Tabulator("#comparablesTable", {
        layout: "fitData",
        columns: getComparablesTableColumns()
    });
}

//=============================================================
//                     7. COLUMN DEFINITIONS
//=============================================================

function getRevenueTableColumns() {
    return [
        { title: "Revenue Source", field: "revenue_source_name", editor: "input" },
        { title: "Price", field: "revenue_source_price", editor: "number", formatter: dollarFormatter },
        {
            title: "Price Source",
            field: "price_source",
            formatter: linkedCellFormatter('price_source_link'),
            editor: "input"
        },
        { title: "# Transactions/Month", field: "monthly_transactions", editor: "number" },
        { title: "Frequency Notes", field: "frequency_notes", editor: "input" },
        {
            title: "Frequency Source",
            field: "frequency_source",
            formatter: linkedCellFormatter('frequency_source_link'),
            editor: "input"
        },
        deleteButtonColumn(() => AppTables.revenueTable)
    ];
}

function getPurchasesTableColumns() {
    return [
        { title: "Cost Item Name", field: "cost_item_name", editor: "input" },
        { title: "Cost Per Unit", field: "cost_per_unit", editor: "number", formatter: dollarFormatter },
        {
            title: "Cost Source",
            field: "cost_source",
            formatter: linkedCellFormatter('cost_source_link'),
            editor: "input"
        },
        { title: "Monthly Transactions", field: "monthly_transactions", editor: "number" },
        { title: "Frequency Notes", field: "frequency_notes", editor: "input" },
        {
            title: "Frequency Source",
            field: "frequency_source",
            formatter: linkedCellFormatter('frequency_source_link'),
            editor: "input"
        },
        deleteButtonColumn(() => AppTables.purchasesTable)
    ];
}

function getEmployeesTableColumns() {
    return [
        { title: "Role", field: "role", editor: "input" },
        { title: "Number", field: "number", editor: "number" },
        { title: "Wage", field: "wage", editor: "number", formatter: dollarFormatter },
        { title: "Wage Frequency", field: "wage_type", editor: "input" },
        { title: "Notes/Assumptions", field: "notes", editor: "input" },
        {
            title: "Source",
            field: "source_string",
            formatter: linkedCellFormatter('source_link'),
            editor: "input"
        },
        deleteButtonColumn(() => AppTables.employeesTable)
    ];
}

function getCapexTableColumns() {
    return [
        { title: "Expense Name", field: "expense_name", editor: "input" },
        { title: "Amount", field: "amount", editor: "number", formatter: dollarFormatter },
        { title: "Purchase Year", field: "purchase_year", editor: "number" },
        { title: "Depreciation Life (years)", field: "depreciation_life", editor: "number" },
        { title: "Notes", field: "notes", editor: "input" },
        {
            title: "Source",
            field: "source_string",
            formatter: linkedCellFormatter('source_link'),
            editor: "input"
        },
        deleteButtonColumn(() => AppTables.capexTable)
    ];
}

function getOpexTableColumns() {
    return [
        { title: "Expense Name", field: "expense_name", editor: "input" },
        { title: "Amount", field: "amount", editor: "number", formatter: dollarFormatter },
        { title: "Frequency", field: "frequency", editor: "input" },
        { title: "Notes", field: "notes", editor: "input" },
        {
            title: "Source",
            field: "source_string",
            formatter: linkedCellFormatter('source_link'),
            editor: "input"
        },
        deleteButtonColumn(() => AppTables.opexTable)
    ];
}

function getHistoricalISTableColumns() {
    return [
        { title: "Year", field: "year", editor: "number" },
        { title: "Revenue", field: "revenue", editor: "number", formatter: dollarFormatter },
        { title: "Cost of Sales", field: "cost_of_sales", editor: "number", formatter: dollarFormatter },
        { title: "Operating Expenses", field: "operating_expenses", editor: "number", formatter: dollarFormatter },
        { title: "EBITDA", field: "ebitda", editor: "number", formatter: dollarFormatter },
        { title: "Depreciation", field: "depreciation", editor: "number", formatter: dollarFormatter },
        { title: "EBIT", field: "ebit", editor: "number", formatter: dollarFormatter },
        { title: "Interest Expense", field: "interest_expense", editor: "number", formatter: dollarFormatter },
        { title: "Income Taxes", field: "income_taxes", editor: "number", formatter: dollarFormatter },
        { title: "Net Income", field: "net_income", editor: "number", formatter: dollarFormatter },
        deleteButtonColumn(() => AppTables.historicalISTable)
    ];
}

function getComparablesTableColumns() {
    return [
        { title: "Company Name", field: "company_name", editor: "input" },
        { title: "Enterprise Value", field: "enterprise_value", editor: "number", formatter: dollarFormatter },
        { title: "Market Cap", field: "market_cap", editor: "number", formatter: dollarFormatter },
        { title: "EBITDA", field: "ebitda", editor: "number", formatter: dollarFormatter },
        { title: "Equity Beta", field: "equity_beta", editor: "number" },
        { title: "Asset Beta", field: "asset_beta", editor: "number" },
        { title: "EV/EBITDA", field: "ev_ebitda_multiple", editor: "number" },
        { title: "Source", field: "source", editor: "input" },
        { title: "Source Date", field: "source_date", editor: "input" },
        deleteButtonColumn(() => AppTables.comparablesTable)
    ];
}

function linkedCellFormatter(linkField) {
    return function(cell) {
        const value = cell.getValue();
        const row = cell.getRow().getData();
        const url = row[linkField];
        return url ? `<a href="${url}" target="_blank">${value}</a>` : value;
    };
}

function deleteButtonColumn(getTableFn) {
    return {
        title: "",
        formatter: () => "<button class='delete-btn'>X</button>",
        width: 80,
        hozAlign: "center",
        cellClick: (e, cell) => {
            cell.getRow().delete();
            const table = getTableFn();
            if (table) table.redraw();
        }
    };
}

//=============================================================
//                     8. DATA MANAGEMENT
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

function refreshTables() {
    loadTableData("revenue", AppTables.revenueTable);
    loadTableData("cost_of_sales", AppTables.purchasesTable);
    loadTableData("operating_expenses", AppTables.opexTable);
    loadTableData("capital_expenditures", AppTables.capexTable);
    loadTableData("employees", AppTables.employeesTable);
    loadTableData("historical_financials", AppTables.historicalISTable);
    loadTableData("comparables", AppTables.comparablesTable);
}

function loadTableData(tableIdentifier, table) {
    fetch(`/api/table_data/${tableIdentifier}`)
        .then(response => response.json())
        .then(responseData => {
            if (responseData.error) {
                console.error(`loadTableData: ${responseData.error}`);
                return;
            }

            // Handle either array or object with root_key
            let tableData = responseData;
            if (responseData.data) {
                tableData = responseData.data;
            }

            // Convert to array if needed
            if (!Array.isArray(tableData)) {
                const rootKey = responseData.root_key;
                tableData = rootKey && tableData[rootKey] ? tableData[rootKey] : [tableData];
            }

            // Filter out empty rows
            tableData = tableData.filter(row => 
                Object.values(row).some(value => value != null && value !== '')
            );

            table.setData(tableData)
                .then(() => {
                    adjustTableHeight(table);
                    console.log(`Table ${tableIdentifier} updated successfully`);
                })
                .catch(error => console.error(`Error setting data for ${tableIdentifier}:`, error));
        })
        .catch(error => {
            console.error(`loadTableData: Error loading ${tableIdentifier}:`, error);
            if (error.response) {
                error.response.json().then(errorData => {
                    console.error(`Server error: ${errorData.error}`);
                });
            }
        });
}

function addRow(table) {
    let newRow = {};

    switch (table) {
        case AppTables.capexTable:
            newRow = {
                expense_name: "",
                amount: 0,
                frequency: "",
                source_link: "",
                source_string: "",
                notes: ""
            };
            break;
        case AppTables.opexTable:
            newRow = {
                expense_name: "",
                amount: 0,
                frequency: "",
                source_string: "",
                source_link: "",
                notes: ""
            };
            break;
        case AppTables.employeesTable:
            newRow = {
                role: "",
                number: 0,
                wage: 0,
                wage_type: "hourly",
                monthly_hours: 0,
                notes: "",
                source_link: "",
                source_string: ""
            };
            break;
        case AppTables.purchasesTable:
            newRow = {
                cost_item_name: "",
                cost_per_unit: 0,
                cost_source: "",
                cost_source_link: "",
                frequency: 0,
                frequency_notes: "",
                frequency_source: "",
                frequency_source_link: ""
            };
            break;
        case AppTables.revenueTable:
            newRow = {
                revenue_source_name: "",
                revenue_source_price: 0,
                price_source: "",
                price_source_link: "",
                frequency: 0,
                frequency_notes: "",
                frequency_source: "",
                frequency_source_link: ""
            };
            break;
        case AppTables.historicalISTable:
            newRow = {
                year: new Date().getFullYear(),
                revenue: 0,
                cost_of_sales: 0,
                operating_expenses: 0,
                ebitda: 0,
                depreciation: 0,
                ebit: 0,
                interest_expense: 0,
                income_taxes: 0,
                net_income: 0
            };
            break;
        case AppTables.comparablesTable:
            newRow = {
                company_name: "",
                enterprise_value: 0,
                market_cap: 0,
                ebitda: 0,
                equity_beta: 0,
                asset_beta: 0,
                ev_ebitda_multiple: 0,
                source: "",
                source_date: ""
            };
            break;
        default:
            console.error("addRow: Unknown table type");
            return;
    }

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
//                     9. UTILITIES & API
//=============================================================

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Populate projects dropdown in Load Project Modal
function populateProjectsDropdown() {
    console.log('populateProjectsDropdown: Function called');
    const dropdown = document.getElementById('existingProjects');
    fetch('/api/context')
        .then(response => response.json())
        .then(contextData => {
            console.log('Context data received:', contextData);
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
        console.log(`Successfully processed ${file.name} with AI.`);
        document.getElementById("aiResponse").innerHTML = `<p>AI Response Text: ${data.text}</p>`;
        row.querySelector('.check-cell').innerHTML = '&#10004;';
        refreshTables();
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
        refreshTables();
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
//                     10. PROJECT MANAGEMENT
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

        // Update project name globally
        project_name = selectedProject;
        project_type = selectedProjectType;

        // Update UI
        updateProjectUI(selectedProject);

        // Refresh all tables
        refreshTables();

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
        
        // Update global variables
        project_name = projectName;
        project_type = projectType;
        
        // Close the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('newProjectModal'));
        if (modal) modal.hide();
        
        // Update UI
        updateProjectUI(projectName);
        
        // Refresh tables and project dropdown
        refreshTables();
        populateProjectsDropdown();
    })
    .catch(error => {
        console.error('createNewProject: Error:', error);
        alert('Error creating project');
    });
}

//=============================================================
//                     11. FILE DOWNLOADS
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

    return Promise.all([response.blob(), Promise.resolve(filename)])
        .then(([blob, filename]) => {
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


// Add to your existing initialization code
function initializeDynamicTables() {
    // Initialize create table button
    const createTableBtn = document.getElementById('createTableBtn');
    if (createTableBtn) {
        createTableBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('newTableModal'));
            modal.show();
        });
    }

    // Initialize create table confirmation
    const createTableConfirm = document.getElementById('createTableConfirm');
    if (createTableConfirm) {
        createTableConfirm.addEventListener('click', handleTableCreation);
    }
}

// Add this to your existing document.addEventListener('DOMContentLoaded', ...)
document.addEventListener('DOMContentLoaded', () => {
    // ... your existing initialization code ...
    initializeDynamicTables();
});

// Function to handle table creation
function handleTableCreation() {
    const tableId = document.getElementById('tableId').value;
    const tableTitle = document.getElementById('tableTitle').value;

    if (!tableId || !tableTitle) {
        alert('Please fill in both Table ID and Title');
        return;
    }

    // Create the table
    createDynamicTable(
        `${tableId}Container`, 
        tableId,
        getDefaultColumns(),
        [],
        tableTitle
    );

    // Close the modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('newTableModal'));
    modal.hide();
}

// Updated createDynamicTable function
function createDynamicTable(containerId, tableId, columns, data = [], title) {
    // Check if table already exists
    if (AppTables[tableId]) {
        console.warn(`Table ${tableId} already exists`);
        return AppTables[tableId];
    }

    // Create container div if it doesn't exist
    let container = document.getElementById(containerId);
    if (!container) {
        container = document.createElement('div');
        container.id = containerId;
        container.className = 'card mb-4';
        
        // Find or create main content area
        let mainContent = document.getElementById('mainContent');
        if (!mainContent) {
            mainContent = document.createElement('div');
            mainContent.id = 'mainContent';
            document.body.appendChild(mainContent);
        }
        mainContent.appendChild(container);
    }

    // Create table structure
    container.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">${title}</h5>
            <div>
                <button class="btn btn-outline-primary btn-sm add-row-btn">
                    Add Row
                </button>
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

    // Initialize Tabulator
    const table = new Tabulator(`#${tableId}`, {
        layout: "fitData",
        autoResize: true,
        columns: columns,
        data: data
    });

    // Add event listeners
    container.querySelector('.add-row-btn').addEventListener('click', () => addRow(table));
    container.querySelector('.ai-btn').addEventListener('click', () => preparePayload(tableId));

    // Store table reference
    AppTables[tableId] = table;

    return table;
}


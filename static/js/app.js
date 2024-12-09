import { clearAllData, uploadPDF, dollarFormatter } from './shared-modules.js';
const PROJECT_NAME = "financial";



let revenueTable;

// Initialize Tabulator for revenue data
revenueTable = new Tabulator("#revenueTable", {
    layout: "fitData",
    autoResize: true,
    columns: [
        {
            title: "Revenue Source",
            field: "revenue_source_name",
            editor: "input"
        },
        {
            title: "Price",
            field: "revenue_source_price", 
            editor: "number",
            formatter: dollarFormatter
        },
        {
            title: "Price Source",
            field: "price_source",
            formatter: function(cell) {
                const source = cell.getValue();
                const row = cell.getRow().getData();
                const url = row.price_source_link;
                return url ? `<a href="${url}" target="_blank">${source}</a>` : source;
            },
            editor: "input"
        },
        {
            title: "# Transactions/Month",
            field: "monthly_transactions",
            editor: "number"
        },
        {
            title: "Frequency Notes",
            field: "frequency_notes",
            editor: "input"
        },
        {
            title: "Frequency Source",
            field: "frequency_source",
            formatter: function(cell) {
                const source = cell.getValue();
                const row = cell.getRow().getData();
                const url = row.frequency_source_link;
                return url ? `<a href="${url}" target="_blank">${source}</a>` : source;
            },
            editor: "input"
        },
        {
            title: "",
            formatter: function() {
                return "<button class='delete-btn'>X</button>";
            },
            width: 80,
            hozAlign: "center",
            cellClick: function(e, cell) {
                cell.getRow().delete();
                revenueTable.redraw();
            }
        }
    ]
});



// Initialize Tabulator table for Inventory and COGS data
const purchasesTable = new Tabulator("#purchasesTable", {
    layout: "fitData", // Fit columns to width of table
    autoResize: true, // Enable auto-resize
    columns: [
        { title: "Cost Item Name", field: "cost_item_name", editor: "input" },
        { title: "Cost Per Unit", field: "cost_per_unit", editor: "number", formatter: dollarFormatter },
        {
            title: "Cost Source",
            field: "cost_source",
            formatter: function(cell) {
                const source = cell.getValue();
                const row = cell.getRow().getData();
                const url = row.cost_source_link;
                return url ? `<a href="${url}" target="_blank">${source}</a>` : source;
            },
            editor: "input"
        },
        { title: "Monthly Transactions", field: "monthly_transactions", editor: "number" },
        { title: "Frequency Notes", field: "frequency_notes", editor: "input" },
        {
            title: "Frequency Source",
            field: "frequency_source",
            formatter: function(cell) {
                const source = cell.getValue();
                const row = cell.getRow().getData();
                const url = row.frequency_source_link;
                return url ? `<a href="${url}" target="_blank">${source}</a>` : source;
            },
            editor: "input"
        },
        {
            title: "",  // Add the delete button
            formatter: function () {
                return "<button class='delete-btn'>X</button>";
            },
            width: 80,
            hozAlign: "center",
            cellClick: function (e, cell) {
                cell.getRow().delete();
                purchasesTable.redraw();
            },
        }
    ]
});




// Initialize Tabulator table for Employees data
const employeesTable = new Tabulator("#employeesTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Role", field: "role", editor: "input" },
        { title: "Number", field: "number", editor: "number" },
        { title: "Wage", field: "wage", editor: "number", formatter: dollarFormatter },
        { title: "Wage Frequency", field: "wage_type", editor: "input" },
		{ title: "Notes/Assumptions", field: "notes", editor: "input" },
        {
            title: "Source", 
            field: "source_string",  // Use source_string as the base field
            formatter: function(cell, formatterParams) {
                // Get the source_string and source_link from the row data
                let sourceString = cell.getValue();  // source_string
                let sourceLink = cell.getRow().getData().source_link;  // source_link
                
                // If both source_string and source_link exist, return a clickable link
                if (sourceLink) {
                    return `<a href="${sourceLink}" target="_blank">${sourceString}</a>`;
                } else {
                    return sourceString;  // Return just the source_string if no link is provided
                }
            },
            editor: "input"  // Allow editing if needed
        },
        {
            title: "", 
            formatter: function() {
                return "<button class='delete-btn'>X</button>";  // Apply the custom class
            },
            width: 80,  // Adjust width to make it proportional
            hozAlign: "center",  // Center the button in the cell
            cellClick: function(e, cell) {
                cell.getRow().delete();  // Delete the row when clicked
                employeesTable.redraw();  // Force redraw in case of layout issues
            }
        }
    ]
});


// Initialize Tabulator table for CAPEX data
const capexTable = new Tabulator("#capexTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Expense Name", field: "expense_name", editor: "input" },
        { title: "Amount", field: "amount", editor: "number", formatter: dollarFormatter },
        { title: "Purchase Year", field: "purchase_year", editor: "number" },
        { title: "Depreciation Life (years)", field: "depreciation_life", editor: "number" },
		{ title: "Notes", field: "notes", editor: "input" },
        {
            title: "Source", 
            field: "source_string",  // Use source_string as the base field
            formatter: function(cell, formatterParams) {
                // Get the source_string and source_link from the row data
                let sourceString = cell.getValue();  // source_string
                let sourceLink = cell.getRow().getData().source_link;  // source_link
                
                // If both source_string and source_link exist, return a clickable link
                if (sourceLink) {
                    return `<a href="${sourceLink}" target="_blank">${sourceString}</a>`;
                } else {
                    return sourceString;  // Return just the source_string if no link is provided
                }
            },
            editor: "input"  // Allow editing if needed
        },
        {
            title: "", 
            formatter: function() {
                return "<button class='delete-btn'>X</button>";  // Apply the custom class
            },
            width: 80,  // Adjust width to make it proportional
            hozAlign: "center",  // Center the button in the cell
            cellClick: function(e, cell) {
                cell.getRow().delete();  // Delete the row when clicked
                capexTable.redraw();  // Force redraw in case of layout issues
            }
        }
    ]
});


// Initialize Tabulator table for OPEX data
const opexTable = new Tabulator("#opexTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Expense Name", field: "expense_name", editor: "input" },
        { title: "Amount", field: "amount", editor: "number", formatter: dollarFormatter },
        { title: "Frequency", field: "frequency", editor: "input" },
        { title: "Notes", field: "notes", editor: "input" },
        {
            title: "Source", 
            field: "source_string",  // Use source_string as the base field
            formatter: function(cell, formatterParams) {
                // Get the source_string and source_link from the row data
                let sourceString = cell.getValue();  // source_string
                let sourceLink = cell.getRow().getData().source_link;  // source_link
                
                // If both source_string and source_link exist, return a clickable link
                if (sourceLink) {
                    return `<a href="${sourceLink}" target="_blank">${sourceString}</a>`;
                } else {
                    return sourceString;  // Return just the source_string if no link is provided
                }
            },
            editor: "input"  // Allow editing if needed
        },
        {
            title: "", 
            formatter: function() {
                return "<button class='delete-btn'>X</button>";  // Apply the custom class
            },
            width: 80,  // Adjust width to make it proportional
            hozAlign: "center",  // Center the button in the cell
            cellClick: function(e, cell) {
                cell.getRow().delete();  // Delete the row when clicked
                opexTable.redraw();  // Force redraw in case of layout issues
            }
        }
    ]
});


// Initialize Tabulator table for Historical Financial Data
const historicalISTable = new Tabulator("#historicalISTable", {
    layout: "fitData",
    columns: [
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
        {
            title: "",
            formatter: function () {
                return "<button class='delete-btn'>X</button>";
            },
            width: 80,
            hozAlign: "center",
            cellClick: function (e, cell) {
                cell.getRow().delete();
                historicalISTable.redraw();
            }
        }
    ]
});



// Initialize Tabulator table for Comparable Companies
const comparablesTable = new Tabulator("#comparablesTable", {
    layout: "fitData",
    columns: [
        { title: "Company Name", field: "company_name", editor: "input" },
        { title: "Enterprise Value", field: "enterprise_value", editor: "number", formatter: dollarFormatter },
        { title: "Market Cap", field: "market_cap", editor: "number", formatter: dollarFormatter },
        { title: "EBITDA", field: "ebitda", editor: "number", formatter: dollarFormatter },
        { title: "Equity Beta", field: "equity_beta", editor: "number" },
        { title: "Asset Beta", field: "asset_beta", editor: "number" },
        { title: "EV/EBITDA", field: "ev_ebitda_multiple", editor: "number" },
        { title: "Source", field: "source", editor: "input" },
        { title: "Source Date", field: "source_date", editor: "input" },
        {
            title: "",
            formatter: function () {
                return "<button class='delete-btn'>X</button>";
            },
            width: 80,
            hozAlign: "center",
            cellClick: function (e, cell) {
                cell.getRow().delete();
                comparablesTable.redraw();
            }
        }
    ]
});


// Function to adjust table height based on visible rows
function adjustTableHeight(table) {
    const rowCount = table.getDataCount("active"); // Get the number of visible rows
    const rowHeight = 35; // Approximate height per row (adjust if needed)
    const headerHeight = 40; // Approximate header height

    // Set the height of the container to fit all visible rows
    const newHeight = Math.min(rowCount * rowHeight + headerHeight, 600); // Limit max height if desired
    table.element.style.height = `${newHeight}px`;
    table.redraw(); // Redraw the table to apply new height
}

document.getElementById('historicalISAIButton').addEventListener('click', function () {
    preparePayload('historicalISTable');
});



// Load table data from backend
refreshTables();

function refreshTables(){
    loadTableData("revenue", revenueTable);
    loadTableData("cost_of_sales", purchasesTable);
    loadTableData("operating_expenses", opexTable);
    loadTableData("capital_expenditures", capexTable);
    loadTableData("employees", employeesTable);
    loadTableData("historical_financials", historicalISTable);
    loadTableData("comparables", comparablesTable);
}

// Function to load table data from the backend with conditional logic based on tableIdentifier
function loadTableData(tableIdentifier, table) {
    fetch(`/api/table_data/${PROJECT_NAME}/${tableIdentifier}`)
        .then(response => response.json())
        .then(responseData => {
            if (!responseData || !responseData.data) {
                console.error(`loadTableData: No data returned for tableIdentifier: ${tableIdentifier}`);
                return;
            }

            const data = responseData.data;
            const rootKey = responseData.root_key;
            
            console.log(`Table: ${tableIdentifier}`);
            console.log('Data received:', data);
            console.log('Root key:', rootKey);

            let tableData;
            
            // If data has the root key, use that array
            if (rootKey && data[rootKey]) {
                tableData = data[rootKey];
            }
            // If data is already an array, use it directly
            else if (Array.isArray(data)) {
                tableData = data;
            }
            // If data is an object but not an array, wrap it
            else if (data && typeof data === 'object') {
                tableData = [data];
            }
            // Fallback to empty array
            else {
                tableData = [];
            }

            // Filter out any empty or null rows
            tableData = tableData.filter(row => {
                // Check if the row has any non-empty values
                return Object.values(row).some(value => 
                    value !== null && value !== undefined && value !== ''
                );
            });

            console.log(`Processed data for ${tableIdentifier}:`, tableData);
            
            // Set the data to the table
            table.setData(tableData)
                .then(() => {
                    adjustTableHeight(table);
                    console.log(`Table ${tableIdentifier} updated successfully`);
                })
                .catch(error => {
                    console.error(`Error setting data for ${tableIdentifier}:`, error);
                });
        })
        .catch(error => {
            console.error(`loadTableData: Error loading ${tableIdentifier} data:`, error);
        });
}


// Versatile function to add a new row to any table based on its column structure
function addRow(table) {
    // Determine the table type and define the row structure accordingly
    let newRow = {};

    if (table === capexTable) {
        // CAPEX table structure
        newRow = {
            expense_name: "",
            amount: 0,
            frequency: "",
            source_link: "",
            source_string: "",
            notes: ""
        };
    } else if (table === opexTable) {
        // OPEX table structure
        newRow = {
            expense_name: "",
            amount: 0,
            frequency: "",
            source_string: "",
            source_link: "",
            notes: ""
        };
    } else if (table === employeesTable) {
        // Employees table structure
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
    } else if (table === purchasesTable) {
        // Cost of sales table structure
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
    } else if (table === revenueTable) {
        // Revenue table structure
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
    } else if (table === historicalISTable) {
        // Historical Income Statement table structure
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
    
    } else if (table === comparablesTable) {
        // Comparables table structure
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
    } else {
        console.error("addRow: Unknown table type. Unable to add row.");
        return;
    }

    // Add the new row to the specified table
    table.addRow(newRow)
        .then(() => {
            table.redraw();  // Force redraw in case of layout issues
        });
}




function preparePayload(updateScope) {
    const payload = {
        updateScope: updateScope, // Either specific table name or "all"
		project_name: PROJECT_NAME, //This variable tells the backend whether it's a financial model or catalyst partners project
        businessDescription: document.getElementById("businessDescription").value,
        userPrompt: document.getElementById("chatgptPrompt").value,
        pdfFileName: updateScope === 'all' ? document.getElementById('uploadedPDFName').value : null // Only include PDF if updating all
    };

    // Automatically call sendToBackend with the constructed payload
    sendToBackend(payload);
}




function sendToBackend(payload) {
    const loadingIcon = document.getElementById("loading");
    const aiResponseDiv = document.getElementById("aiResponse");

    loadingIcon.style.display = "block";  
    aiResponseDiv.innerHTML = "";  

    fetch('/api/openai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => {
        loadingIcon.style.display = "none";  

        // Display the AI response text
        aiResponseDiv.innerHTML = `<p>AI Response Text: ${data.text}</p>`;

        // Reload each table to fetch updated data from the backend JSON files
        refreshTables();
    })
    .catch(error => {
        loadingIcon.style.display = "none";
        aiResponseDiv.innerHTML = `<p>Error occurred: ${error.message}</p>`;
        console.error('sendToBackend: Error:', error);
    });
}






// For individual table buttons
document.getElementById('capexAIButton').addEventListener('click', function() {
    preparePayload('capexTable');
});

document.getElementById('opexAIButton').addEventListener('click', function() {
    preparePayload('opexTable');
});

document.getElementById('revenueAIButton').addEventListener('click', function() {
    preparePayload('revenueTable');
});

document.getElementById('purchasesAIButton').addEventListener('click', function() {
    preparePayload('purchasesTable');
});

// Call this function after uploading a PDF successfully
function initializePdfAIButtonListener() {
    const pdfAIButton = document.getElementById('pdfAIButton');
    if (pdfAIButton) {
        pdfAIButton.addEventListener('click', function() {
            preparePayload('all');
        });
    } else {
        console.error("initializePdfAIButtonListener: pdfAIButton not found.");
    }
}


//Actions following click on excel button
document.getElementById('downloadExcelButton').addEventListener('click', function() {
    fetch(`/download_excel?project_name=${PROJECT_NAME}`, {
        method: 'GET',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error downloading Excel file: ' + response.statusText);
        }
        // Get filename from Content-Disposition header
        const filename = response.headers.get('Content-Disposition')
            ?.split(';')
            ?.find(n => n.includes('filename='))
            ?.replace('filename=', '')
            ?.trim() || 'model.xlsx';
            
        return Promise.all([response.blob(), Promise.resolve(filename)]);
    })
    .then(([blob, filename]) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();  // Programmatically click the anchor to trigger download
        a.remove();
        window.URL.revokeObjectURL(url); // Clean up the URL object
    })
    .catch(error => console.error('downloadExcelButton click handler: Error:', error));
});

//Actions following click on powerpoint button
document.getElementById('downloadPPTButton').addEventListener('click', function() {
    fetch(`/download_ppt?project_name=${PROJECT_NAME}`, {
        method: 'GET',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error downloading PowerPoint file: ' + response.statusText);
        }
        // Get filename from Content-Disposition header
        const filename = response.headers.get('Content-Disposition')
            ?.split(';')
            ?.find(n => n.includes('filename='))
            ?.replace('filename=', '')
            ?.trim() || 'presentation.pptx';
            
        return Promise.all([response.blob(), Promise.resolve(filename)]);
    })
    .then(([blob, filename]) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();  // Programmatically click the anchor to trigger download
        a.remove();
        window.URL.revokeObjectURL(url); // Clean up the URL object
    })
    .catch(error => console.error('downloadPPTButton click handler: Error:', error));
});



// Handle files and update the uploaded documents table
function handleFiles(event) {
	let uploadedFiles = [];
    const files = event.target.files;
    const tableBody = document.getElementById('uploadedDocsTable').querySelector('tbody');

    Array.from(files).forEach(file => {
        if (file.type === "application/pdf") {
            // Add the file to the uploadedFiles array
            uploadedFiles.push({ name: file.name, status: "Pending" });

            // Create a new row for each file
            const row = document.createElement('tr');

            // File Name Column
            const fileNameCell = document.createElement('td');
            fileNameCell.textContent = file.name;
            row.appendChild(fileNameCell);

            // Upload to AI Column with Centered Button
            const uploadCell = document.createElement('td');
            const uploadButton = document.createElement('button');
            uploadButton.innerHTML = '<span style="font-family: Arial, sans-serif;">&#x2728;</span>'; // AI sparkle icon
            uploadButton.onclick = () => uploadToAI(file.name, row); // Pass file name and row for updating the check mark
            uploadCell.appendChild(uploadButton);
            row.appendChild(uploadCell);

            // Check Column (Initially Empty, Updated on Upload)
            const checkCell = document.createElement('td');
            checkCell.classList.add("check-cell");  // Add class for styling if needed
            row.appendChild(checkCell);

            // Remove Column with Remove Button
            const removeCell = document.createElement('td');
            const removeButton = document.createElement('button');
            removeButton.textContent = 'X';
            removeButton.onclick = () => row.remove();  // Remove the row from the table
            removeCell.appendChild(removeButton);
            row.appendChild(removeCell);

            // Append the row to the table body
            tableBody.appendChild(row);
			
			// Call uploadPDF to upload the selected PDF file
            uploadPDF(file);
        }
    });
}

// Move this outside of DOMContentLoaded to make it a standalone function
function initializeUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const pdfInput = document.getElementById('pdfUpload');

    if (!uploadZone || !pdfInput) {
        console.error("Upload elements not found");
        return;
    }

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => {
            uploadZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => {
            uploadZone.classList.remove('dragover');
        });
    });

    // Handle dropped files
    uploadZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    });

    // Handle click to upload
    uploadZone.addEventListener('click', () => {
        pdfInput.click();
    });

    // Handle file input change
    pdfInput.addEventListener('change', handleFiles);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Call initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    initializeUploadZone();
    initializeAddRowButtons();
});




// Attach the clearAllData function to the button
document.getElementById('clearDataButton').addEventListener('click', () => {
    clearAllData(PROJECT_NAME);
});


// Function to handle uploading the file to AI and update checkmark
function uploadToAI(fileName, row) {
    console.log(`Uploading ${fileName} to AI...`);

    // Show the loading spinner
    const loadingIcon = document.getElementById("loading");
    loadingIcon.style.display = "block";

    // Prepare the payload for the backend API
    const payload = {
        pdfFileName: fileName,
		projectName: PROJECT_NAME,
        userPrompt: document.getElementById("chatgptPrompt").value, // Add user prompt to payload
        updateScope: 'all' // Explicitly set the update scope to 'all' for full context processing
    };

    // Send the request to the backend to process the PDF
    fetch('/api/openai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        // Hide the loading spinner
        loadingIcon.style.display = "none";

        if (data.error) {
            alert(`Error uploading ${fileName}: ${data.error}`);
        } else {
            console.log(`Successfully uploaded ${fileName} to AI.`);
            
            // Update the AI response section
            const aiResponseDiv = document.getElementById("aiResponse");
            aiResponseDiv.innerHTML = `<p>AI Response Text: ${data.text}</p>`;

            // Mark file as sent with a checkmark in the Check column
            const checkCell = row.querySelector('.check-cell');
            checkCell.innerHTML = '&#10004;';  // Unicode checkmark symbol
            
            // Reload each table to fetch updated data from the backend JSON files
            refreshTables();
        }
    })
    .catch(error => {
        // Hide the loading spinner in case of error
        loadingIcon.style.display = "none";
        console.error('uploadToAI: Error uploading ${fileName} to AI:', error);
    });
}

// Function to initialize "Add Row" buttons for all tables
function initializeAddRowButtons() {
    // Find all buttons with class 'button-outline' and attach click handlers
    document.querySelectorAll('.button-outline').forEach(button => {
        button.addEventListener('click', (e) => {
            console.log('Add Row button clicked');
            // Find the table container ID by traversing up to card div and finding table-container
            const tableId = e.target.closest('.card').querySelector('.table-container').id;
            
            // Get the Tabulator table instance associated with this container
            // findTable returns array of matching tables, we want the first one
            const table = Tabulator.findTable(`#${tableId}`)[0];
            
            // If we found a valid table, add a new empty row to it
            if (table) {
                addRow(table); // addRow() is defined elsewhere and handles table-specific row structures
            }
        });
    });
}

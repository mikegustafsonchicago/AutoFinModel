import { clearAllData } from './shared-modules.js';
import { uploadPDF } from './shared-modules.js';
import { dollarFormatter } from './shared-modules.js';


const PROJECT_NAME = "financial";

const revenueTable = new Tabulator("#revenueTable", {
    layout: "fitData", // Fit columns to width of table
	autoResize: true, // Enable auto-resize
    dataTree: true, // Enable tree structure
    dataTreeChildField: "ingredients", // Define the field that contains child rows (ingredients in this case)
    dataTreeStartExpanded: false, // Start with all rows collapsed initially
    columns: [
        // Recipe-level columns (Parent level)
        { title: "Recipe Name", field: "name", editor: "input" },  // Recipe name
        { title: "Price", field: "price", editor: "number", formatter: dollarFormatter },      // Recipe price
        { title: "Price Notes", field: "price_notes", editor: "input" }, // Recipe notes

        // Ingredient-level columns (Child level shown when expanded)
        { title: "Ingredient ID", field: "ingredient_id", editor: "input", visible: false }, 
        { title: "Ingredient Name", field: "ingredient_name", editor: "input" }, 
        { title: "Unit", field: "unit", editor: "input" }, 
        { title: "Amount", field: "amount", editor: "number" }, 
        { title: "Price per Unit", field: "price", editor: "number", formatter: dollarFormatter }, 
        { title: "Notes", field: "notes", editor: "input" }, 

        // Add a delete button for both recipe and ingredients
        {
            title: "",  // Add the delete button
            formatter: function () {
                return "<button class='delete-btn'>X</button>";
            },
            width: 80,
            hozAlign: "center",
            cellClick: function (e, cell) {
                cell.getRow().delete();
                revenueTable.redraw();
            }
        }
    ]
});

// Set up rowClick dynamically after the table is built
revenueTable.on("tableBuilt", function() {
    // Expand all rows to make sure all are accessible
    revenueTable.getData().forEach(row => revenueTable.getRow(row).treeExpand());
});



// Initialize Tabulator tree structure for Inventory and COGS data
const purchasesTable = new Tabulator("#purchasesTable", {
    layout: "fitData", // Fit columns to width of table
	autoResize: true, // Enable auto-resize
    dataTree: true, // Enable tree structure
    dataTreeChildField: "price_data_raw", // Define the field that contains child rows
    dataTreeStartExpanded: false, // Start with all rows collapsed
    columns: [
        // Parent columns
        { title: "Ingredient ID", field: "ingredient_id", editor: "input"},
        { title: "Name", field: "ingredient_name", editor: "input" },
        
        // Child Columns
        { title: "Unit Name", field: "unit_name", editor: "input" }, 
        { title: "Company", field: "company", editor: "input" },
        { title: "Unit", field: "unit", editor: "input" },
        { title: "Price", field: "price", editor: "number", formatter: dollarFormatter },
        { title: "Selling Quantity", field: "selling_quantity", editor: "number" },
        {
            title: "Source",
            field: "source",
            formatter: function (cell, formatterParams) {
                let sourceString = cell.getValue();
                return sourceString ? `<a href="https://${sourceString}" target="_blank">${sourceString}</a>` : sourceString;
            },
            editor: "input",
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

// Set up rowClick dynamically after the table is built
purchasesTable.on("tableBuilt", function() {
    // Expand all rows to make sure all are accessible
    purchasesTable.getData().forEach(row => purchasesTable.getRow(row).treeExpand());
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
                historicalFinancialsTable.redraw();
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
	loadTableData("purchases", purchasesTable);
	loadTableData("OPEX", opexTable);
	loadTableData("CAPEX", capexTable);
	loadTableData("employees", employeesTable);
	loadTableData("historicalIS", historicalISTable); // Add this line
}

// Function to load table data from the backend with conditional logic based on tableIdentifier
function loadTableData(tableIdentifier, table) {
    fetch(`/api/table_data/${PROJECT_NAME}/${tableIdentifier}`)
        .then(response => response.json())
        .then(data => {
            if (!data) {
                console.error(`No data returned for tableIdentifier: ${tableIdentifier}`);
                return;
            }

            switch (tableIdentifier) {
                case "revenue":
                    if (Array.isArray(data.recipes)) {
                        table.setData(data.recipes); // Use the "recipes" key for revenue
                    } else {
                        console.error('Invalid data structure for revenueTable.');
                    }
                    break;

                case "purchases":
                    if (Array.isArray(data.purchases_table)) {
                        table.setData(data.purchases_table); // Use "purchases_table" for purchases
                    } else {
                        console.error('Invalid data structure for purchasesTable.');
                    }
                    break;

                case "CAPEX":
                case "OPEX":
                    if (Array.isArray(data.expenses)) {
                        table.setData(data.expenses); // Use "expenses" array for CAPEX/OPEX
                    } else {
                        console.error(`Invalid data structure for ${tableIdentifier}.`);
                    }
                    break;

                case "employees":
                    if (Array.isArray(data.employees)) {
                        table.setData(data.employees); // Use "employees" array for employeesTable
                    } else {
                        console.error('Invalid data structure for employeesTable.');
                    }
                    break;

                case "historicalIS":
                    if (Array.isArray(data.historical_financials)) {
                        table.setData(data.historical_financials); // Use "historical_financials" array for historicalIS
                    } else {
                        console.error('Invalid data structure for historicalISTable.');
                    }
                    break;

                default:
                    console.error('Error in loadTableData: Unknown table identifier:', tableIdentifier);
                    break;
            }
        })
        .catch(error => {
            console.error('Error in loadTableData: Error loading table data:', error);
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
            purchase_year: new Date().getFullYear(),
            depreciation_life: 0,
            notes: "",
            source_string: "",
            source_link: ""
        };
    } else if (table === opexTable) {
        // OPEX table structure
        newRow = {
            expense_name: "",
            amount: 0,
            frequency: "",
            notes: "",
            source_string: "",
            source_link: ""
        };
	
	} else if (table === employeesTable) {
        // Employees table structure
        newRow = {
            role: "",
            number: 0,
			wage: 0,
            wage_type: "salary",
            notes: "",
            source_string: "",
            source_link: ""
        };
    } else if (table === purchasesTable) {
        // Purchases table structure with nested data
        newRow = {
            ingredient_id: 0,  // Parent row data
            name: "New Ingredient",
            price_data_raw: [  // Child rows data for the tree structure
                {
                    company: "",
                    price: 0,
                    selling_quantity: 0,
                    source: "",
                    unit: "",
                    unit_name: ""
                }
            ]
        };
	} else if (table === historicalFinancialsTable) {
		// Historical Financials table structure
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
    } else {
        console.error("Unknown table type. Unable to add row.");
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
        console.error('Error:', error);
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
        console.error("pdfAIButton not found.");
    }
}


//Actions following click on excel button
document.getElementById('downloadExcelButton').addEventListener('click', function() {
    fetch('/download_excel', {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) {
            return response.blob();  // Convert response to blob for file download
        } else {
            console.error('Error downloading Excel file:', response.statusText);
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'financial_model.xlsx';  // The default file name
        document.body.appendChild(a);
        a.click();  // Programmatically click the anchor to trigger download
        a.remove();
    })
    .catch(error => console.error('Error:', error));
});



document.addEventListener('DOMContentLoaded', function() {
    const uploadZone = document.getElementById('uploadZone');
    const pdfInput = document.getElementById('pdfUpload');

    if (uploadZone && pdfInput) {
        // Trigger file input on click
        uploadZone.addEventListener('click', () => pdfInput.click());

        // Handle drag-and-drop files
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.add('dragover');
        });
        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('dragover');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            handleFiles({ target: { files: files } });
        });
		// Handle files selected via the dialog
        pdfInput.addEventListener('change', (e) => {
            handleFiles(e); // Pass the event directly to handleFiles
        });
    } else {
        console.error("Upload elements not found.");
    }
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



// Attach the clearAllData function to the button
document.getElementById('clearDataButton').addEventListener('click', clearAllData);


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
        console.error(`Error uploading ${fileName} to AI:`, error);
    });
}




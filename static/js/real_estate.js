import { clearAllData, uploadFile, dollarFormatter } from './shared-modules.js';
const project_type = "real_estate";



let propertyTable;

// Initialize Tabulator for property fundamentals data
propertyTable = new Tabulator("#propertyTable", {
    layout: "fitData",
    autoResize: true,
    columns: [
        {
            title: "Address",
            field: "address",
            editor: "input"
        },
        {
            title: "Municipality", 
            field: "municipality",
            editor: "input"
        },
        {
            title: "Parcel ID",
            field: "parcel_id",
            editor: "input"
        },
        {
            title: "Approximate Acreage",
            field: "approximate_acreage",
            editor: "input"
        },
        {
            title: "Current Use",
            field: "current_use",
            editor: "input"
        },
        {
            title: "Zoning",
            field: "zoning",
            editor: "input"
        },
        {
            title: "Water/Sewer",
            field: "water_sewer",
            editor: "input"
        },
        {
            title: "Electricity",
            field: "electricity",
            editor: "input"
        },
        {
            title: "Availability",
            field: "availability",
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
                propertyTable.redraw();
            }
        }
    ]
});



// Initialize Tabulator table for Property Zoning data
const zoningTable = new Tabulator("#zoningTable", {
    layout: "fitData", // Fit columns to width of table
    autoResize: true, // Enable auto-resize
    columns: [
        { title: "Property Description", field: "property_description", editor: "input" },
        { title: "Jurisdiction", field: "jurisdiction", editor: "input" },
        { title: "Site Conditions", field: "site_conditions", editor: "input" },
        { title: "Current Zoning", field: "current_zoning", editor: "input" },
        { title: "Density Detail", field: "density_detail", editor: "input" },
        { title: "Access", field: "access", editor: "input" },
        { title: "Flood Zone", field: "flood_zone", editor: "input" },
        { title: "Water/Sewer", field: "water_sewer", editor: "input" },
        { title: "Electric", field: "electric", editor: "input" },
        {
            title: "",  // Add the delete button
            formatter: function () {
                return "<button class='delete-btn'>X</button>";
            },
            width: 80,
            hozAlign: "center",
            cellClick: function (e, cell) {
                cell.getRow().delete();
                zoningTable.redraw();
            },
        }
    ]
});




// Initialize Tabulator table for Property Financials data
const propertyFinancialsTable = new Tabulator("#propertyFinancialsTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "NOI", field: "noi", editor: "number", formatter: dollarFormatter },
        { title: "Monthly Rent", field: "rent_monthly", editor: "number", formatter: dollarFormatter },
        { title: "Rentable Sq Ft", field: "rentable_sqft", editor: "number" },
        { title: "Land Area (Acres)", field: "land_area", editor: "number" },
        { title: "Tenant Name", field: "tenant_name", editor: "input" },
        { title: "Website", field: "website", editor: "input" },
        { title: "Guarantor", field: "guarantor", editor: "input" },
        { title: "Ownership Type", field: "ownership_type", editor: "input" },
        { title: "Lease Type", field: "lease_type", editor: "input" },
        { title: "Landlord Responsibilities", field: "landlord_responsibilities", editor: "input" },
        { title: "Store Open Date", field: "store_open_date", editor: "input" },
        { title: "Lease Term Remaining", field: "lease_term_remaining", editor: "number" },
        { title: "Rent Commencement", field: "rent_commencement", editor: "input" },
        { title: "Lease Expiration", field: "lease_expiration", editor: "input" },
        { title: "Rent Increases", field: "rent_increases", editor: "input" },
        { title: "Options", field: "options", editor: "input" },
        {
            title: "", 
            formatter: function() {
                return "<button class='delete-btn'>X</button>";  // Apply the custom class
            },
            width: 80,  // Adjust width to make it proportional
            hozAlign: "center",  // Center the button in the cell
            cellClick: function(e, cell) {
                cell.getRow().delete();  // Delete the row when clicked
                propertyFinancialsTable.redraw();  // Force redraw in case of layout issues
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





// Load table data from backend
refreshTables();

function refreshTables(){
    loadTableData("property_fundamentals", propertyTable);
    loadTableData("property_zoning", zoningTable); 
    loadTableData("property_financials", propertyFinancialsTable);
}

// Function to load table data from the backend with conditional logic based on tableIdentifier
function loadTableData(tableIdentifier, table) {
    fetch(`/api/table_data/${project_type}/${tableIdentifier}`)
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

    if (table === propertyTable) {
        newRow = {
            address: "",
            municipality: "",
            parcel_id: "",
            approximate_acreage: "",
            current_use: "",
            zoning: "",
            water_sewer: "",
            electricity: "",
            availability: ""
        };
    } else if (table === zoningTable) {
        newRow = {
            property_description: "",
            jurisdiction: "",
            site_conditions: "",
            current_zoning: "",
            density_detail: "",
            access: "",
            flood_zone: "",
            water_sewer: "",
            electric: ""
        };
    } else if (table === propertyFinancialsTable) {
        newRow = {
            noi: 0,
            rent_monthly: 0,
            rentable_sqft: 0,
            land_area: 0,
            tenant_name: "",
            website: "",
            guarantor: "",
            ownership_type: "",
            lease_type: "",
            landlord_responsibilities: "",
            store_open_date: "",
            lease_term_remaining: 0,
            rent_commencement: "",
            lease_expiration: "",
            rent_increases: "",
            options: ""
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
		project_type: project_type, //This variable tells the backend whether it's a financial model or catalyst partners project
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
document.getElementById('propertyAIButton').addEventListener('click', function() {
    preparePayload('propertyTable');
});

document.getElementById('zoningAIButton').addEventListener('click', function() {
    preparePayload('zoningTable');
});

document.getElementById('propertyFinancialsAIButton').addEventListener('click', function() {
    preparePayload('propertyFinancialsTable');
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

//Actions following click on powerpoint button
document.getElementById('downloadPPTButton').addEventListener('click', function() {
    fetch(`/download_ppt?project_type=${project_type}`, {
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
			
			// Call uploadFile to upload the selected PDF file
            uploadFile(file, project_type);
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
    clearAllData(project_type);
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
		projectName: project_type,
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

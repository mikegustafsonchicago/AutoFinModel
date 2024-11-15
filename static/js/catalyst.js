const PROJECT_NAME = "catalyst";

// Initialize Tabulator table for Fundamentals data
const fundamentalsTable = new Tabulator("#fundamentalsTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Name", field: "firm_name", editor: "input" },
        { title: "Founded", field: "founded_year", editor: "number" },
        { title: "Primary Office", field: "primary_office", editor: "number" },
        { title: "Ownership", field: "ownership_structure", editor: "input" },
		{ title: "Employees", field: "total_employees", editor: "input" },
		{ title: "Diversity Status", field: "diversity_status", editor: "input" },
        {
            title: "Website",
            field: "website",  // Website as a clickable link
            formatter: function(cell, formatterParams) {
                let websiteText = cell.getValue();
                let sourceLink = cell.getRow().getData().source_link;
                if (sourceLink) {
                    return `<a href="${sourceLink}" target="_blank">${websiteText}</a>`;
                } else {
                    return websiteText;
                }
            },
            editor: "input"  // Allow editing if needed
        },
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
        }
    ]
});

// Set up rowClick dynamically after the table is built
fundamentalsTable.on("tableBuilt", function() {
    // Expand all rows to make sure all are accessible
    fundamentalsTable.getData().forEach(row => fundamentalsTable.getRow(row).treeExpand());
});


// Initialize Tabulator table for Investment Team data
const investmentTeamTable = new Tabulator("#investmentTeamTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Key Personnel", field: "investment_team_member_name", editor: "input" },
        { title: "Title", field: "investment_team_member_title", editor: "input" },
        { title: "Joined Firm", field: "investment_team_member_join_date", editor: "number" },
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
                investmentTeamTable.redraw();  // Force redraw in case of layout issues
            }
        }
    ]
});


// Initialize Tabulator table for Fund Fees & Key Terms data
const feesKeyTermsTable = new Tabulator("#feesKeyTermsTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Currency", field: "currency", editor: "input" },
        { title: "Target Fundraise", field: "target_fundraise", editor: "number" },
        { title: "Management Fee", field: "management_fee", editor: "number" },
        { title: "Carried Interest", field: "carried_interest", editor: "number" },
		{ title: "Preferred Return", field: "preferred_return", editor: "input" },
		{ title: "Investment Period", field: "investment_period", editor: "input" },
		{ title: "Fund Term", field: "fund_term", editor: "input" },
		{ title: "GP Commitment", field: "GP_commitment", editor: "input" },
		{ title: "GP Commitment Funding Source", field: "GP_commitment_source", editor: "input" },
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
                feesKeyTermsTable.redraw();  // Force redraw in case of layout issues 
            }
        }
    ]
});





// Initialize Tabulator table for Seed Terms data
const seedTermsTable = new Tabulator("#seedTermsTable", {
    layout: "fitData",  // Fit columns to width of table
    columns: [
        { title: "Target Seed Investment", field: "expense_name", editor: "input" },
		{ title: "Initial Seed Investment", field: "expense_name", editor: "input" },
        { title: "Seed Fundraising Timeline", field: "fundraising_date", editor: "number" },
        { title: "Revenue Share", field: "revenue_share", editor: "input" },
        { title: "Revenus Share Cap", field: "revenue_share_cap", editor: "input" },
		{ title: "Revenus Share Tail", field: "revenue_share_tail", editor: "input" },
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
                seedTermsTable.redraw();  // Force redraw in case of layout issues
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
	loadTableData("fundamentals", fundamentalsTable);
	loadTableData("seedTerms", seedTermsTable);
	loadTableData("feesKeyTerms", feesKeyTermsTable);
	loadTableData("investmentTeam", investmentTeamTable);
}

// Function to load table data from the backend with conditional logic based on tableIdentifier
function loadTableData(tableIdentifier, table) {
    fetch(`/api/table_data/${PROJECT_NAME}/${tableIdentifier}`)
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                table.setData(data);
            } else {
                console.error(`Invalid data structure for ${tableIdentifier}.`);
            }
        })
        .catch(error => {
            console.error('Error loading table data:', error);
        });
}






// Versatile function to add a new row to any table based on its column structure
function addRow(table) {
    // Determine the table type and define the row structure accordingly
    let newRow = {};

    if (table === feesKeyTermsTable) {
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
    } else if (table === seedTermsTable) {
        // OPEX table structure
        newRow = {
            expense_name: "",
            amount: 0,
            frequency: "",
            notes: "",
            source_string: "",
            source_link: ""
        };
	
	} else if (table === investmentTeamTable) {
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
document.getElementById('feesKeyTermsAIButton').addEventListener('click', function() {
    preparePayload('feesKeyTermsTable');
});

document.getElementById('seedTermsAIButton').addEventListener('click', function() {
    preparePayload('seedTermsTable');
});

document.getElementById('fundamentalsAIButton').addEventListener('click', function() {
    preparePayload('fundamentalsTable');
});

document.getElementById('investmentTeamTable').addEventListener('click', function() {
    preparePayload('investmentTeamTable');
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


// Actions following click on excel button
document.getElementById('downloadExcelButton').addEventListener('click', function() {
    const projectName = PROJECT_NAME;  

    fetch(`/download_excel?project_name=${encodeURIComponent(projectName)}`, {  // Append project_name as a query parameter
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
        a.download = 'Catalyst_Partners_Summary.xlsx';  // The default file name
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


// Function to handle clearing all data
function clearAllData() {
    const payload = { projectName: PROJECT_NAME }; // Send as an object

    fetch('/api/clear_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload) // Correctly stringify the object
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Notify the user
        location.reload();    // Reload the page to refresh tables
    })
    .catch(error => {
        console.error('Error clearing data:', error);
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
        userPrompt: document.getElementById("chatgptPrompt").value, // Add user prompt to payload
		projectName: PROJECT_NAME,
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




// Upload the PDF file to the "Uploads" folder
function uploadPDF(pdfFile) {
    const formData = new FormData();
    formData.append("pdf", pdfFile);
	console.log(formData)
    // Send the file to the backend
    fetch('/api/upload_pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('PDF upload response:', data);

        if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error uploading PDF:', error);
    });
}


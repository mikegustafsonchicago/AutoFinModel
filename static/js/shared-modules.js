// Function to handle clearing all data
export  function clearAllData(PROJECT_NAME) {
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


// Upload the PDF file to the "Uploads" folder
export function uploadPDF(pdfFile) {
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


export function dollarFormatter(cell, formatterParams, onRendered) {
    const value = cell.getValue(); // Get the unformatted cell value
    if (value === null || value === undefined) return "$0"; // Handle empty or undefined values
    return `$${parseFloat(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

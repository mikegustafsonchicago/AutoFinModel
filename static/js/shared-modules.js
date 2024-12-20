// Function to handle clearing all data
export  function clearAllData(project_name, project_type) {
    const payload = { projectName: project_name, projectType: project_type }; // Send as an object

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
export function uploadFile(upload_file, project_name, project_type) {
    const formData = new FormData();
    formData.append("file", upload_file);
    formData.append("projectName", project_name);
    formData.append("projectType", project_type);
    console.log(formData)
    // Send the file to the backend
    fetch('/api/upload_file', {
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

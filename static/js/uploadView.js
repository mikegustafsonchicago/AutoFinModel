// This app manages the DOM elements related to the file upload zone.
// It handles the UI interactions for uploading files, displaying them in a table,
// and managing drag & drop functionality.

//=============================================================
//                     1. INITIALIZATION
//=============================================================

import { UploadManager } from './uploadManager.js';

export class UploadView {
    /**
     * Initialize the UploadView with a new UploadManager instance
     * The UploadManager handles the business logic while this class manages the UI
     */
    constructor(uploadManager, stateManager) {
        this.uploadManager = uploadManager;
        this.stateManager = stateManager;
        
        // Bind methods
        this.handleFiles = this.handleFiles.bind(this);
        this.preventDefaults = this.preventDefaults.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.updateFileList = this.updateFileList.bind(this);
    }

    async initialize() {
        try {
            // First, get DOM elements
            this.uploadZone = document.getElementById('uploadZone');
            this.pdfInput = document.getElementById('pdfUpload');
            this.tableBody = document.getElementById('uploadedDocsTable')?.querySelector('tbody');

            if (!this.uploadZone || !this.pdfInput || !this.tableBody) {
                throw new Error('Required upload elements not found');
            }

            // Then set up UI
            await this.setupUploadZoneUI();
            
            // After UI is set up, add event listeners
            await this.setupEventListeners();
            
            // Subscribe to state changes AFTER DOM elements are ready
            this.stateManager.subscribe((state) => {
                if (state.current_project?.uploaded_files) {
                    this.updateFileList(state.current_project.uploaded_files);
                }
            });
            
            // Finally, load any existing files
            await this.loadExistingFiles();
            
            return true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Set up initial UI state of the upload zone
     * Displays default text prompt for users to drop or click to upload files
     */
    setupUploadZoneUI() {
        if (!this.uploadZone) {
            return;
        }
        
        // Clear any existing content
        this.uploadZone.innerHTML = `
            <div class="upload-prompt">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Drop PDF files here or click to upload</p>
            </div>
        `;
        
        // Add visual feedback styles
        this.uploadZone.classList.add('upload-zone');
    }

    /**
     * Load and display any existing uploaded files from the server
     * Fetches context data which includes previously uploaded files
     * Creates table rows for each existing file
     */
    async loadExistingFiles() {
        try {
            const files = this.uploadManager.getUploadedFiles();
            this.updateFileList(files);
        } catch (error) {
            this.stateManager.setState({
                application: { error: 'Error loading existing files' }
            });
        }
    }

    /**
     * Set up all event listeners for drag & drop and file upload functionality
     * Handles:
     * - Preventing default browser drag/drop behavior
     * - Visual feedback during drag operations
     * - File drop and click-to-upload functionality
     */
    setupEventListeners() {
        // Double-check elements exist
        if (!this.uploadZone || !this.pdfInput) {
            return;
        }

        const events = ['dragenter', 'dragover', 'dragleave', 'drop'];
        
        // Remove any existing listeners first
        events.forEach(eventName => {
            this.uploadZone.removeEventListener(eventName, this.preventDefaults);
            document.body.removeEventListener(eventName, this.preventDefaults);
        });
        
        // Add new listeners
        events.forEach(eventName => {
            this.uploadZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Add visual feedback
        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadZone.addEventListener(eventName, () => {
                this.uploadZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadZone.addEventListener(eventName, () => {
                this.uploadZone.classList.remove('dragover');
            }, false);
        });

        // Handle drops
        this.uploadZone.addEventListener('drop', (e) => {
            this.preventDefaults(e);
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        }, false);

        // Handle clicks
        this.uploadZone.addEventListener('click', () => {
            this.pdfInput.click();
        }, false);

        this.pdfInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        }, false);
    }

    async handleFiles(files) {
        try {
            const currentProject = this.stateManager.getCurrentProject();
            
            if (!currentProject?.name) {
                this.stateManager.updateErrorUI('Please select a project first');
                return;
            }

            for (const file of Array.from(files)) {
                if (file.type === 'application/pdf') {
                    try {
                        // Upload the file
                        await this.uploadManager.handlePdfUpload(
                            file,
                            currentProject.name,
                            currentProject.type
                        );
                        
                        // Get fresh state after upload
                        const newState = this.stateManager.getState();
                        
                        // Force refresh the file list
                        const uploadedFiles = this.uploadManager.getUploadedFiles();
                        
                        // Update the UI
                        this.updateFileList(uploadedFiles);
                        
                        // Add visual feedback
                        this.addSuccessIndicator(file.name);
                        
                    } catch (error) {
                        this.stateManager.updateErrorUI(`Failed to upload ${file.name}: ${error.message}`);
                    }
                }
            }
        } catch (error) {
            this.stateManager.updateErrorUI('Error handling files');
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Create a new table row to display an uploaded file
     * @param {Object} file - The file object containing at least a name property
     * @returns {HTMLTableRowElement} A table row with file info and control buttons
     * 
     * Creates a row with 4 columns:
     * 1. File name
     * 2. AI processing button (sparkle emoji)
     * 3. Status check indicator
     * 4. Remove file button
     */
    createFileRow(file) {
        const row = document.createElement('tr');
        
        // Column 1: File name display
        const fileNameCell = document.createElement('td');
        fileNameCell.textContent = file.name;
        row.appendChild(fileNameCell);

        // Column 2: AI processing button with sparkle emoji
        const uploadCell = document.createElement('td');
        const uploadButton = document.createElement('button');
        uploadButton.innerHTML = '<span style="font-family: Arial, sans-serif;">&#x2728;</span>';
        uploadButton.onclick = () => this.uploadManager.sendFileToAI(file, row);
        uploadCell.appendChild(uploadButton);
        row.appendChild(uploadCell);

        // Column 3: Status check indicator
        const checkCell = document.createElement('td');
        checkCell.classList.add("check-cell");
        row.appendChild(checkCell);

        // Column 4: Remove file button
        const removeCell = document.createElement('td');
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm';
        removeButton.innerHTML = '<i class="fas fa-times"></i>';
        removeButton.onclick = async () => {
            try {
                const currentProject = this.stateManager.getCurrentProject();
                if (!currentProject?.name) {
                    throw new Error('No project selected');
                }
                
                // Show loading state
                removeButton.disabled = true;
                removeButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                // Delete the file
                await this.uploadManager.deleteFile(file.name, currentProject.name);
                
                // Get fresh list of files and update UI
                const updatedFiles = this.uploadManager.getUploadedFiles();
                this.updateFileList(updatedFiles);
                
            } catch (error) {
                this.stateManager.updateErrorUI(`Failed to delete file: ${error.message}`);
                
                // Reset button state
                removeButton.disabled = false;
                removeButton.innerHTML = '<i class="fas fa-times"></i>';
            }
        };
        removeCell.appendChild(removeButton);
        row.appendChild(removeCell);

        return row;
    }

    // Add visual feedback for successful deletion
    showDeleteSuccess(filename) {
        const successMessage = document.createElement('div');
        successMessage.className = 'alert alert-success alert-dismissible fade show mt-2';
        successMessage.innerHTML = `
            Successfully deleted: ${filename}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page (adjust selector as needed)
        document.querySelector('#uploadZone').appendChild(successMessage);
        
        // Remove after 3 seconds
        setTimeout(() => {
            successMessage.remove();
        }, 3000);
    }

    // Update the updateFileList method to be more robust
    updateFileList(files) {
        if (!this.tableBody) {
            return;
        }
        
        // Clear existing rows
        this.tableBody.innerHTML = '';
        
        // Convert input to array and remove duplicates
        let fileArray;
        if (Array.isArray(files)) {
            fileArray = [...new Set(files)];
        } else if (typeof files === 'object' && files !== null) {
            fileArray = [...new Set(Object.values(files))];
        } else {
            fileArray = [];
        }
        
        if (fileArray.length === 0) {
            this.showEmptyState();
            return;
        }
        
        fileArray.forEach(filename => {
            if (filename && typeof filename === 'string') {
                const row = this.createFileRow({name: filename});
                this.tableBody.appendChild(row);
            }
        });
    }

    showEmptyState() {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="4" class="text-center text-muted">
                No files uploaded yet
            </td>
        `;
        this.tableBody.appendChild(emptyRow);
    }

    // Add visual feedback for successful upload
    addSuccessIndicator(filename) {
        // Find the row for this file
        const row = Array.from(this.tableBody.querySelectorAll('tr'))
            .find(row => row.querySelector('td')?.textContent === filename);
        
        if (row) {
            const checkCell = row.querySelector('.check-cell');
            if (checkCell) {
                checkCell.innerHTML = '<i class="fas fa-check text-success"></i>';
                // Remove the indicator after 3 seconds
                setTimeout(() => {
                    checkCell.innerHTML = '';
                }, 3000);
            }
        }
    }
}

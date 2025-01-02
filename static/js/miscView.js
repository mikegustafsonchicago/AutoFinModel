// This file contains miscellaneous views that don't fit into other categories
// Handles UI elements like error messages, project headers, download buttons and sidebar

import { StateManager } from './stateManager.js';


export class MiscView {
    constructor(miscManager, stateManager) {
        // Store references to managers that handle business logic
        this.miscManager = miscManager;
        this.stateManager = stateManager;
        
        // Define labels for different types of downloadable outputs
        this.OUTPUT_BUTTON_LABELS = {
            excel_model: "Download Financial Model (xlsx)",
            powerpoint_overview: "Download Investment Overview (pptx)", 
            excel_overview: "Download Overview (xlsx)"
        };
    }

    initialize() {
        try {
            // Set up initial UI state
            this.updateProjectNameHeader();
            this.updateDownloadButtons();
            this.setupSidebarToggle();
        } catch (error) {
            console.error('MiscView: Initialization failed:', error);
        }
    }

    // Display error messages in a container at the top of the page
    showErrorMessage(message) {
        const errorContainer = document.getElementById('errorContainer') || this.createErrorContainer();
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }

    // Create error container if it doesn't exist
    createErrorContainer() {
        const container = document.createElement('div');
        container.id = 'errorContainer';
        container.className = 'alert alert-danger';
        document.body.insertBefore(container, document.body.firstChild);
        return container;
    }

    // Update the header to show current project name
    updateProjectNameHeader() {
        const projectNameHeader = document.getElementById('projectNameHeader');
        if (projectNameHeader) {
            const { name } = this.stateManager.getCurrentProject();
            projectNameHeader.textContent = name || '';
        }
    }

    // Refresh download buttons based on available outputs for current project
    updateDownloadButtons() {
        const container = document.getElementById('downloadButtonsContainer');
        if (!container) {
            console.warn('MiscView: Download buttons container not found');
            return;
        }

        // Clear existing buttons
        container.innerHTML = '';
        
        const currentProject = this.stateManager.getCurrentProject();
        if (!currentProject) {
            console.warn('MiscView: No current project found');
            return;
        }

        // Get list of available output types for this project type
        const availableOutputs = currentProject.outputs;

        if (availableOutputs.length > 0) {
            // Create a download button for each available output type
            availableOutputs.forEach(outputType => {
                const buttonLabel = this.OUTPUT_BUTTON_LABELS[outputType] || outputType;
                this.addDownloadButton(
                    container, 
                    buttonLabel,
                    outputType,
                    currentProject.name
                );
            });
        } else {
            // Show message if no outputs are available
            const message = document.createElement('p');
            message.className = 'text-muted';
            message.textContent = 'Generate outputs to enable downloads';
            container.appendChild(message);
        }
    }

    // Create and configure a download button for a specific output type
    addDownloadButton(container, text, outputType, projectName) {
        const button = document.createElement('button');
        button.className = 'btn btn-success mb-2';
        button.style.width = '100%';
        button.textContent = text;
        
        // Handle click event to download the file
        button.addEventListener('click', async () => {
            try {
                // Get file blob and suggested filename from miscManager
                const { blob, filename } = await this.miscManager.handleDownload(projectName, outputType);
                
                // Create temporary link and trigger download
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                
                // Clean up
                window.URL.revokeObjectURL(url);
                a.remove();
            } catch (error) {
                console.error(`MiscView: Download failed for ${outputType}:`, error);
                this.showErrorMessage('Failed to download file');
            }
        });

        container.appendChild(button);
    }

    // Set up toggle functionality for sidebar collapse/expand
    setupSidebarToggle() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mainContent = document.getElementById('mainContent');
        
        sidebarToggle?.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            // Adjust main content padding based on sidebar state
            mainContent.style.paddingLeft = sidebar.classList.contains('collapsed') ? '60px' : '20px';
        });
    }
}

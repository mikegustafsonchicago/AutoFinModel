// This file contains miscellaneous views that don't fit into other categories
// Handles UI elements like error messages, project headers, download buttons and sidebar

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

        // Bind methods that will be used as event handlers
        this.updateProjectNameHeader = this.updateProjectNameHeader.bind(this);
        this.updateDownloadButtons = this.updateDownloadButtons.bind(this);

        // Subscribe to state changes
        this.stateManager.subscribe((state) => {
            this.updateProjectNameHeader();
            this.updateDownloadButtons();
        });
    }

    initialize() {
        try {
            // Set up initial UI state
            this.updateProjectNameHeader();
            this.updateDownloadButtons();
            this.setupSidebarToggle();
        } catch (error) {
            this.showErrorMessage('Failed to initialize UI components');
        }
    }

    // Display error messages in a container at the top of the page
    showErrorMessage(message) {
        const errorContainer = document.getElementById('errorContainer') || this.createErrorContainer();
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';

        // Update application state to reflect error
        this.stateManager.setState({
            application: {
                error: message
            }
        });
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
            const currentProject = this.stateManager.getCurrentProject();
            projectNameHeader.textContent = currentProject?.name || '';
        }
    }

    /**
     * Updates the download buttons container based on available outputs for the current project.
     * This method handles three main cases:
     * 1. No container found - logs warning and exits
     * 2. No current project - displays welcome message
     * 3. Has current project - creates download buttons for each available output type
     */
    updateDownloadButtons() {
        const container = document.getElementById('downloadButtonsContainer');
        if (!container) {
            return;
        }

        container.innerHTML = '';
        const currentProject = this.stateManager.getCurrentProject();
        
        if (!currentProject?.name) {
            const message = document.createElement('p');
            message.className = 'text-muted';
            message.textContent = 'Create a project to get started';
            container.appendChild(message);
            return;
        }

        // Get available outputs and convert to array if needed
        const availableOutputs = currentProject.available_outputs || {};

        // Convert to array if it's an object
        const outputsArray = Array.isArray(availableOutputs) 
            ? availableOutputs 
            : Object.values(availableOutputs);

        if (outputsArray && outputsArray.length > 0) {
            outputsArray.forEach(outputType => {
                const buttonLabel = this.OUTPUT_BUTTON_LABELS[outputType] || outputType;
                this.addDownloadButton(
                    container, 
                    buttonLabel,
                    outputType,
                    currentProject.name
                );
            });
        } else {
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
                // Update loading state
                this.stateManager.setState({
                    application: {
                        loading: true
                    }
                });

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

                // Clear loading state
                this.stateManager.setState({
                    application: {
                        loading: false,
                        error: null
                    }
                });
            } catch (error) {
                this.showErrorMessage('Failed to download file');
                
                // Update error state
                this.stateManager.setState({
                    application: {
                        loading: false,
                        error: `Failed to download ${outputType}: ${error.message}`
                    }
                });
            }
        });

        container.appendChild(button);
    }

    // Set up toggle functionality for sidebar collapse/expand
    setupSidebarToggle() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mainContent = document.getElementById('mainContent');
        
        if (!sidebar || !sidebarToggle || !mainContent) {
            return;
        }

        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            // Adjust main content padding based on sidebar state
            mainContent.style.paddingLeft = sidebar.classList.contains('collapsed') ? '60px' : '20px';
        });
    }
}

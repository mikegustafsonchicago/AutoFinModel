// This app manages the DOM elements related to the project view.
// It handles creating, loading, and managing projects in the UI.

//=============================================================
//                     1. INITIALIZATION
//=============================================================

import { ProjectManager } from './projectManager.js';

export class ProjectView {
    /**
     * Initialize the project view with a project manager instance
     */
    constructor(projectManager) {
        // Inject projectManager instead of creating it
        this.projectManager = projectManager;
        
        // Bind methods that will be used as event handlers
        this.handleRowClick = this.handleRowClick.bind(this);
        this.handleLoadProject = this.handleLoadProject.bind(this);
        this.handleDeleteProject = this.handleDeleteProject.bind(this);
        this.handleCreateProject = this.handleCreateProject.bind(this);
        this.populateProjectsTable = this.populateProjectsTable.bind(this);
        this.updateProjectsTable = this.updateProjectsTable.bind(this);
        this.showNewProjectModal = this.showNewProjectModal.bind(this);

        // Subscribe to state changes
        this.projectManager.stateManager.subscribe((state) => {
            this.updateProjectsTable(state.user.portfolio.projects);
        });
    }

    async initialize() {
        // Get DOM elements
        this.projectsTable = document.getElementById('existingProjectsTable')?.querySelector('tbody');
        this.projectTypeDropdown = document.getElementById('projectType');
        this.createProjectBtn = document.getElementById('createProjectBtn');
        this.newProjectModal = document.getElementById('newProjectModal');

        if (!this.projectsTable || !this.projectTypeDropdown || !this.newProjectModal) {
            console.error('ProjectView: Required project elements not found');
            return false;
        }

        // Initialize event listeners
        this.initializeEventListeners();

        try {
            await Promise.all([
                this.populateProjectsTable(),
                this.populateNewProjectTypeDropdown()
            ]);
            return true;
        } catch (error) {
            console.error('ProjectView: Initialization failed:', error);
            return false;
        }
    }

    initializeEventListeners() {
        // Create project button
        if (this.createProjectBtn) {
            this.createProjectBtn.addEventListener('click', this.handleCreateProject);
        }
    }

    async handleCreateProject() {
        const projectNameInput = document.getElementById('newProjectName');
        const projectTypeSelect = document.getElementById('projectType');
        
        const projectName = projectNameInput?.value?.trim();
        const projectType = projectTypeSelect?.value;

        if (!projectName || !projectType) {
            alert('Please enter both project name and type');
            return;
        }

        try {
            const success = await this.projectManager.createNewProject(projectName, projectType);
            
            if (success) {
                // Clear inputs
                projectNameInput.value = '';
                projectTypeSelect.value = '';
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('newProjectModal'));
                modal?.hide();

                // Refresh table
                this.populateProjectsTable();
            }
        } catch (error) {
            console.error('ProjectView: Error creating project:', error);
            alert('Failed to create project. Please try again.');
        }
    }

   /**
     * Populate the existing projects table with data from the server.
     * Fetches context data and creates table rows for each project.
     * Handles both cases where projects exist and where no projects exist yet.
     */
    async populateProjectsTable() {
        // Validate table element exists in DOM
        if (!this.projectsTable) {
            console.warn('ProjectView: projectsTable element not found');
            return;
        }

        try {
            // Fetch project data from server
            const { projects, metadata, projectTypes } = await this.projectManager.getProjectsData();
            
            // Clear existing table contents
            this.projectsTable.innerHTML = '';
            
            // Store metadata and project types for later use
            this.projectMetadata = metadata || {};
            this.projectData = projectTypes || {};
            
            // Handle case where no projects exist yet
            if (!projects || projects.length === 0) {
                this.showEmptyProjectsMessage();
                return;
            }
            
            // Create and append row for each existing project
            projects.forEach(project => {
                const row = this.createProjectRow(project);
                this.projectsTable.appendChild(row);
            });
        } catch (error) {
            console.error('ProjectView: Error populating projects table:', error);
            this.showErrorState();
        } 
    }

    /**
     * Populates the project type dropdown menu for new project creation.
     * This method:
     * 1. Fetches available project types from the server's context API endpoint
     * 2. Clears any existing dropdown options
     * 3. Adds a default "Select type" option as the first choice
     * 4. Populates the remaining options with available project types
     * 
     * The dropdown is used in the new project creation modal to let users
     * select what type of project they want to create (e.g. real_estate, 
     * financial, etc).
     */
    async populateNewProjectTypeDropdown() {
        console.log('ProjectView: Starting populateNewProjectTypeDropdown');
        
        if (!this.projectTypeDropdown) {
            console.warn('ProjectView: Project type dropdown element not found in DOM');
            return;
        }
        
        try {
            console.log('ProjectView: Clearing existing dropdown options');
            // Clear existing options
            this.projectTypeDropdown.innerHTML = '';
            
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select project type';
            this.projectTypeDropdown.appendChild(defaultOption);
            

            // Get project types from ProjectManager
            const projectTypes = await this.projectManager.getProjectTypes();

            
            // Check if we have project types
            if (Object.keys(projectTypes).length > 0) {
                // Iterate over the object entries
                Object.entries(projectTypes).forEach(([label, value]) => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = label;
                    this.projectTypeDropdown.appendChild(option);
                });
            } else {
                console.warn('ProjectView: No project types received from server');
            }
        } catch (error) {
            console.error('ProjectView: Error populating project type dropdown:', error);
        }
    }

    /**
     * Update the projects table with new project data
     * @param {Array} projects - Array of project objects to display
     */
    async updateProjectsTable(projects) {
        if (!this.projectsTable) return;
        
        this.projectsTable.innerHTML = '';
        
        // Ensure projects is an array
        const projectsArray = Array.isArray(projects) ? projects : [];
        
        if (projectsArray.length === 0) {
            this.showEmptyProjectsMessage();
            return;
        }
        
        projectsArray.forEach(project => {
            const row = this.createProjectRow(project);
            this.projectsTable.appendChild(row);
        });
    }

    handleRowClick(row) {
        document.querySelectorAll('#existingProjectsTable tbody tr')
            .forEach(r => r.classList.remove('selected'));
        row.classList.add('selected');
    }

    handleLoadProject(projectName) {
        this.projectManager.loadProject(projectName)
          .then(() => {
            // Now that the state has changed, either call populate or update
            this.populateProjectsTable();
          })
          .catch(error => console.error(error));
    }
      

    handleDeleteProject(projectName) {
        this.projectManager.deleteProject(projectName)
          .then(() => {
            // Re-populate table after delete
            this.populateProjectsTable();
          })
          .catch(error => console.error(error));
    }
      

    /**
     * Create a table row for a single project
     * @param {Object} project - Project data to display in row
     * @returns {HTMLTableRowElement} The created table row
     */
    createProjectRow(projectName) {
        const row = document.createElement('tr');
        const state = this.projectManager.stateManager.getState();
        
        // Ensure projects is an array
        const projects = Array.isArray(state.user?.portfolio?.projects) 
            ? state.user.portfolio.projects 
            : [];
        
        // Simple equality check instead of find since we just have strings
        const projectData = projects.includes(projectName) ? projectName : null;
        const metadata = state.current_project?.metadata || {};
        
        // Create name column
        const nameCell = document.createElement('td');
        nameCell.textContent = projectName;
        row.appendChild(nameCell);
        
        // Create type column
        const typeCell = document.createElement('td');
        typeCell.textContent = state.current_project?.type || '-';
        row.appendChild(typeCell);
        
        // Create dates columns
        this.addDateColumns(row, metadata);
        
        // Create action buttons
        this.addActionButtons(row, projectName);

        // Add click handler to highlight selected row
        row.addEventListener('click', () => this.handleRowClick(row));
        
        return row;
    }

    addDateColumns(row, metadata) {
        // Created date
        const createdCell = document.createElement('td');
        if (metadata.created_at) {
            createdCell.textContent = new Date(metadata.created_at).toLocaleDateString();
        } else {
            createdCell.textContent = '-';
        }
        row.appendChild(createdCell);
        
        // Modified date
        const modifiedCell = document.createElement('td');
        if (metadata.last_modified_at) {
            modifiedCell.textContent = new Date(metadata.last_modified_at).toLocaleDateString();
        } else {
            modifiedCell.textContent = '-';
        }
        row.appendChild(modifiedCell);
    }

    addActionButtons(row, projectName) {
        // Load button
        const loadCell = document.createElement('td');
        const loadButton = document.createElement('button');
        loadButton.className = 'btn btn-primary btn-sm';
        loadButton.textContent = 'Load';
        
        // Check if this is the current project
        const currentProject = this.projectManager.stateManager.getCurrentProject()?.name;
        if (projectName === currentProject) {
            loadButton.disabled = true;
            loadButton.className = 'btn btn-secondary btn-sm';
            loadButton.textContent = 'Active';
        }
        
        loadButton.addEventListener('click', () => this.handleLoadProject(projectName));
        loadCell.appendChild(loadButton);
        row.appendChild(loadCell);
        
        // Delete button
        const deleteCell = document.createElement('td');
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => this.handleDeleteProject(projectName));
        deleteCell.appendChild(deleteButton);
        row.appendChild(deleteCell);
    }

    showEmptyProjectsMessage() {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="6" class="text-center text-muted">
                No projects created yet. Create a new project to get started.
            </td>
        `;
        this.projectsTable.appendChild(emptyRow);
    }

    showErrorState() {
        this.projectsTable.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    Error loading projects. Please try refreshing the page.
                </td>
            </tr>
        `;
    }

    showNewProjectModal() {
        if (this.newProjectModal) {
            const modal = new bootstrap.Modal(this.newProjectModal);
            modal.show();
        } else {
            console.error('ProjectView: New project modal element not found');
        }
    }
}

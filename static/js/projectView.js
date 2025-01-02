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

                // Refresh projects table
                await this.populateProjectsTable();
            }
        } catch (error) {
            console.error('ProjectView: Error creating project:', error);
            alert('Failed to create project. Please try again.');
        }
    }

    /**
     * Populate the existing projects table with data from the server
     * Fetches context data and creates table rows for each project
     */
    async populateProjectsTable() {
        if (!this.projectsTable) {
            console.warn('ProjectView: projectsTable element not found');
            return;
        }

        try {
            const response = await fetch('/api/context');
            const contextData = await response.json();
            
            this.projectsTable.innerHTML = '';
            
            // Initialize storage objects
            this.projectMetadata = {};
            this.projectData = {};
            
            // Process each project
            contextData.available_projects.forEach(project => {
                // Get metadata with defaults for legacy projects
                this.projectMetadata[project] = {
                    created_at: null,
                    last_modified_at: null,
                    project_type: 'real_estate',  // Default type
                    ...contextData.project_metadata?.[project]  // Spread operator will override defaults if they exist
                };
                
                // Store project type
                this.projectData[project] = contextData.project_types?.[project] || 'real_estate';
            });
            
            contextData.available_projects.forEach(project => {
                const row = this.createProjectRow(project);
                this.projectsTable.appendChild(row);
            });
        } catch (error) {
            console.error('ProjectView: Error loading context:', error);
        }
    }

    /**
     * Populate the project type dropdown for new project creation
     * Fetches available project types from server context
     */
    async populateNewProjectTypeDropdown() {
        if (!this.projectTypeDropdown) {
            console.warn('ProjectView: Project type dropdown not found');
            return;
        }
        
        try {
            const response = await fetch('/api/context');
            const contextData = await response.json();
            
            this.projectTypeDropdown.innerHTML = '';
            
            // Add a default "Select type" option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select project type';
            this.projectTypeDropdown.appendChild(defaultOption);
            
            // Add each project type as an option
            contextData.project_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                this.projectTypeDropdown.appendChild(option);
            });
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
        projects.forEach(project => {
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
        this.projectManager.loadProject(projectName);
    }

    handleDeleteProject(project) {
        this.projectManager.deleteProject(project);
    }

    /**
     * Create a table row for a single project
     * @param {Object} project - Project data to display in row
     * @returns {HTMLTableRowElement} The created table row
     */
    createProjectRow(project) {
        const row = document.createElement('tr');
        
        // Create name column
        const nameCell = document.createElement('td');
        nameCell.textContent = project;
        row.appendChild(nameCell);
        
        // Create type column
        const typeCell = document.createElement('td');
        typeCell.textContent = this.projectData[project] || '-';
        row.appendChild(typeCell);
        
        // Create created date column
        const createdCell = document.createElement('td');
        const metadata = this.projectMetadata?.[project] || {};
        if (metadata.created_at) {
            const createdDate = new Date(metadata.created_at);
            createdCell.textContent = createdDate.toLocaleDateString();
        } else {
            createdCell.textContent = '-';
        }
        row.appendChild(createdCell);
        
        // Create last modified column
        const modifiedCell = document.createElement('td');
        if (metadata.last_modified_at) {
            const modifiedDate = new Date(metadata.last_modified_at);
            modifiedCell.textContent = modifiedDate.toLocaleDateString();
        } else {
            modifiedCell.textContent = '-';
        }
        row.appendChild(modifiedCell);
        
        // Create load button column with bound handler
        const loadCell = document.createElement('td');
        const loadButton = document.createElement('button');
        loadButton.className = 'btn btn-primary btn-sm';
        loadButton.textContent = 'Load';
        
        // Check if this is the current project and disable button if it is
        const currentProject = this.projectManager.stateManager.getCurrentProject()?.name;
        if (project === currentProject) {
            loadButton.disabled = true;
            loadButton.className = 'btn btn-secondary btn-sm';
            loadButton.textContent = 'Active';
        }
        
        loadButton.addEventListener('click', () => this.handleLoadProject(project));
        loadCell.appendChild(loadButton);
        row.appendChild(loadCell);
        
        // Create delete button column with bound handler
        const deleteCell = document.createElement('td');
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => this.handleDeleteProject(project));
        deleteCell.appendChild(deleteButton);
        row.appendChild(deleteCell);

        // Add click handler to highlight selected row
        row.addEventListener('click', () => this.handleRowClick(row));
        
        return row;
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

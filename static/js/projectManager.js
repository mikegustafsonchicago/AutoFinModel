// This file manages the project load/delete/create functionality
import { StateManager } from './stateManager.js';
import { ApiService } from './apiService.js';

export class ProjectManager {
    constructor(stateManager, miscManager) {
        this.stateManager = stateManager;
        this.miscManager = miscManager;
    }

    // Load an existing project
    async loadProject(projectName) {
        if (!projectName) {
            throw new Error('Please select a project');
        }

        try {
            // Update loading state
            this.stateManager.setState({
                application: {
                    loading: true,
                    error: null
                }
            });

            // Use ApiService to load project
            const data = await ApiService.loadProject(projectName);

            if (data.error) {
                throw new Error(data.error);
            }

            // Get current state to preserve user data
            const currentState = this.stateManager.getState();

            // Update state with complete project structure
            this.stateManager.setState({
                current_project: {
                    name: data.projectName,
                    type: data.projectType,
                    metadata: data.metadata || {
                        created_at: new Date().toISOString(),
                        last_modified_at: new Date().toISOString()
                    },
                    available_tables: data.available_tables || [],
                    uploaded_files: data.uploaded_files || [],
                    available_outputs: data.available_outputs || [],
                    gallery: data.gallery || []
                },
                application: {
                    ...currentState.application,
                    loading: false,
                    error: null
                }
            });
            
            // Refresh the page after successful load
            window.location.reload();
            
            return true;
        } catch (error) {
            this.stateManager.setState({
                application: {
                    loading: false,
                    error: `Failed to load project: ${error.message}`
                }
            });
            throw error;
        }
    }

    // Create a new project
    async createNewProject(projectName, projectType) {
        if (!projectName) {
            throw new Error('Please enter a project name');
        }

        if (!projectType) {
            throw new Error('Please select a project type');
        }

        try {
            // Get current state to check for duplicate names
            const currentState = this.stateManager.getState();
            const existingProjects = Array.isArray(currentState.user?.portfolio?.projects) 
                ? currentState.user.portfolio.projects 
                : [];

            // Check for duplicate project name
            if (existingProjects.includes(projectName)) {
                throw new Error('A project with this name already exists. Please choose a different name.');
            }

            // Update loading state
            this.stateManager.setState({
                application: {
                    loading: true,
                    error: null
                }
            });

            const response = await ApiService.createProject({
                projectName,
                projectType
            });

            if (response.error) {
                throw new Error(response.error);
            }

            // Update state with new project and add to portfolio
            this.stateManager.setState({
                current_project: {
                    name: projectName,
                    type: projectType,
                    metadata: {
                        created_at: new Date().toISOString(),
                        last_modified_at: new Date().toISOString()
                    },
                    available_tables: [],
                    uploaded_files: [],
                    available_outputs: [],
                    gallery: []
                },
                user: {
                    ...currentState.user,
                    portfolio: {
                        ...currentState.user.portfolio,
                        projects: [...existingProjects, projectName]
                    }
                },
                application: {
                    ...currentState.application,
                    loading: false,
                    error: null
                }
            });

            return true;
        } catch (error) {
            this.stateManager.setState({
                application: {
                    loading: false,
                    error: `Failed to create project: ${error.message}`
                }
            });
            throw error;
        }
    }

    // Delete a project
    async deleteProject(projectName) {
        if (!projectName) {
            throw new Error('Please select a project to delete');
        }

        // Confirm deletion with user
        if (!confirm(`Are you sure you want to delete project "${projectName}"? This cannot be undone.`)) {
            return false;
        }

        try {
            // Update loading state
            this.stateManager.setState({
                application: {
                    loading: true,
                    error: null
                }
            });

            const response = await ApiService.deleteProject({
                items: [{
                    type: 'project',
                    name: projectName
                }]
            });

            if (response.error) {
                throw new Error(response.error);
            }

            // Get current state
            const currentState = this.stateManager.getState();

            // Clear current project if it was the one deleted
            if (currentState.current_project?.name === projectName) {
                this.stateManager.clearCurrentProject();
            }
            
            // Get existing projects object
            const existingProjects = currentState.user.portfolio.projects || {};
            
            // Create new projects object without the deleted project
            const updatedProjects = {...existingProjects};
            delete updatedProjects[projectName];

            // Update user's portfolio with new projects object
            this.stateManager.setState({
                user: {
                    ...currentState.user,
                    portfolio: {
                        ...currentState.user.portfolio,
                        projects: updatedProjects
                    }
                },
                application: {
                    ...currentState.application,
                    loading: false,
                    error: null
                }
            });

            return true;
        } catch (error) {
            this.stateManager.setState({
                application: {
                    loading: false,
                    error: `Failed to delete project: ${error.message}`
                }
            });
            throw error;
        }
    }

    /**
     * Fetches and processes project data from the server context API endpoint.
     */
    async getProjectsData() {
        try {
            const contextData = await ApiService.fetchContext();
            
            return {
                projects: contextData.user.portfolio.projects,
                metadata: contextData.current_project?.metadata || null,
                projectTypes: contextData.application.available_project_types
            };
        } catch (error) {
            throw error;
        }
    }

    /**
     * Fetches available project types from the context API
     * @returns {Promise<string[]>} Array of project type strings
     */
    async getProjectTypes() {
        try {
            const contextData = await ApiService.fetchContext();
            return contextData.application.available_project_types || [];
        } catch (error) {
            throw error;
        }
    }
}
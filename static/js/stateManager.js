/**
 * Manages application state and UI updates
 * Implements a simple pub/sub pattern for state changes
 */
import { ApiService } from './apiService.js';

export class StateManager {
    /**
     * Initialize state manager with default values
     * Sets up empty listeners Set for pub/sub pattern
     */
    constructor() {
        // Core application state
        this.state = {
            initialized: false, // Whether app has completed initialization
            loading: true,     // Whether app is currently loading data
            error: null,       // Any error messages to display
            user: null         // Current user information
        };
        // Set of subscriber callbacks to notify of state changes
        this.listeners = new Set();
        
        // Project state
        this.currentProject = null;
        this.projectType = null;
        this.availableOutputs = [];
        this.errorContainer = document.getElementById('errorContainer');
        
        // Add valid project types
        this.validProjectTypes = ['financial', 'real_estate', 'catalyst'];
    }

    /**
     * Get current state (returns copy to prevent direct mutation)
     * @returns {Object} Copy of current state
     */
    getState() {
        return {...this.state};
    }

    /**
     * Update state and notify all listeners
     * @param {Object} updates - Object with state properties to update
     */
    setState(updates) {
        // Validate updates before applying
        if (updates.hasOwnProperty('user') && !updates.user) {
            console.warn('Attempting to set null user');
        }

        if (updates.hasOwnProperty('initialized') && 
            updates.initialized && 
            !this.validateStateConsistency()) {
            console.error('Cannot initialize with invalid state');
            return;
        }

        this.state = { ...this.state, ...updates };
        this.notifyListeners();
    }

    /**
     * Add listener for state changes
     * @param {Function} listener - Callback to run on state change
     * @returns {Function} Cleanup function to remove listener
     */
    subscribe(listener) {
        this.listeners.add(listener);
        // Return cleanup function
        return () => this.listeners.delete(listener);
    }

    /**
     * Notify all listeners of state change
     * Passes current state to each listener
     */
    notifyListeners() {
        this.listeners.forEach(listener => listener(this.state));
    }

    

    /**
     * Get current project information
     * @returns {Object} Object containing project name and type
     */
    getCurrentProject() {
        return this.currentProject || {};
    }

    /**
     * Update current project and refresh UI
     * @param {string} projectName - Project name
     * @param {string} projectType - Project type
     * @param {Array} outputs - Available outputs for this project type
     */
    setCurrentProject(project) {
        const validation = this.validateProject(project);
        
        if (!validation.isValid) {
            console.error('Invalid project data:', validation.errors);
            this.updateErrorUI(validation.errors.join('\n'));
            return false;
        }

        try {
            this.currentProject = {
                name: project.name,
                type: project.type,
                outputs: project.outputs || []
            };
            
            // Validate state consistency
            if (!this.validateStateConsistency()) {
                this.clearCurrentProject();
                return false;
            }
            
            console.log('Project set:', this.currentProject);
            return true;
        } catch (error) {
            console.error('Error setting project:', error);
            this.updateErrorUI('Failed to set project: ' + error.message);
            return false;
        }
    }

    /**
     * Clear current project information
     */
    clearCurrentProject() {
        this.currentProject = null;
        this.projectType = null;
        this.setState({
            initialized: false,
            loading: false,
            error: null
        });
    }

    async initialize() {
        console.log('StateManager: Starting initialization');
        try {
            // Use ApiService instead of direct fetch
            const context = await ApiService.fetchContext();
            
            // Set username in state
            this.setState({
                ...this.state,
                user: context.username
            });
            
            // Set initial state if there's a current project and it exists
            if (context.current_project) {
                if (context.available_projects.includes(context.current_project)) {
                    this.currentProject = {
                        name: context.current_project,
                        type: context.project_info?.type,
                        outputs: context.available_outputs || []
                    };
                } else {
                    console.warn(`Current project ${context.current_project} not found in available projects`);
                    // Fall back to first available project if any exist
                    if (context.available_projects.length > 0) {
                        const fallbackProject = context.available_projects[0];
                        console.log(`Falling back to project: ${fallbackProject}`);
                        // Use ApiService.loadProject instead of direct fetch
                        const projectInfo = await ApiService.loadProject(fallbackProject);
                        
                        this.currentProject = {
                            name: fallbackProject,
                            type: projectInfo.type,
                            outputs: projectInfo.available_outputs || []
                        };
                    }
                }
            }

            return context;
        } catch (error) {
            console.error('StateManager: Initialization failed:', error);
            throw error;
        }
    }

    updateErrorUI(message) {
        if (!this.errorContainer) {
            console.error('Error container not found');
            return;
        }

        this.errorContainer.textContent = message;
        this.errorContainer.style.display = 'block';

        // Hide after 5 seconds
        setTimeout(() => {
            this.errorContainer.style.display = 'none';
        }, 5000);
    }

    /**
     * Validates project data before setting
     * @param {Object} project - Project data to validate
     * @returns {Object} - { isValid: boolean, errors: string[] }
     */
    async validateProject(project) {
        const errors = [];
        
        // Check required fields
        if (!project) {
            errors.push('Project data is required');
            return { isValid: false, errors };
        }
        
        if (!project.name) {
            errors.push('Project name is required');
        }
        
        if (!project.type) {
            errors.push('Project type is required');
        } else if (!this.validProjectTypes.includes(project.type)) {
            errors.push(`Invalid project type. Must be one of: ${this.validProjectTypes.join(', ')}`);
        }
        
        if (!Array.isArray(project.outputs)) {
            errors.push('Project outputs must be an array');
        }

        // Verify project exists in projects folder by checking context
        try {
            const context = await ApiService.fetchContext();
            if (!context.available_projects.includes(project.name)) {
                errors.push('Project does not exist in projects folder');
            }
        } catch (error) {
            console.error('Error validating project existence:', error);
            errors.push('Could not verify project existence');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate consistency between different state properties
     */
    validateStateConsistency() {
        if (!this.currentProject) {
            return true; // No project is a valid state
        }

        // Check project type matches available outputs
        if (this.currentProject.type === 'financial' && 
            !this.currentProject.outputs.some(output => 
                ['income_statement', 'balance_sheet', 'cash_flow'].includes(output))) {
            this.updateErrorUI('Financial project must have financial statement outputs');
            return false;
        }

        // Check user permissions (example)
        if (!this.state.user) {
            this.updateErrorUI('No user logged in');
            return false;
        }

        return true;
    }
}

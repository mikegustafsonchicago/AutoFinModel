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
        // Core application state matching backend session structure
        this.state = {
            user: {
                username: null,
                is_authenticated: false,
                portfolio: {
                    projects: []
                }
            },
            current_project: {
                name: null,
                type: null,
                metadata: null,
                available_tables: [],
                uploaded_files: [],
                available_outputs: [],
                gallery: []
            },
            application: {
                available_project_types: [],
                is_initialized: false,
                loading: false,
                error: null
            }
        };

        // Set of subscriber callbacks to notify of state changes
        this.listeners = new Set();
    }

    /**
     * Get current state (returns copy to prevent direct mutation)
     * @returns {Object} Copy of current state
     */
    getState() {
        return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * Update state and notify all listeners
     * @param {Object} updates - Object with state properties to update
     */
    setState(updates) {
        // Deep merge updates with current state
        this.state = this.deepMerge(this.state, updates);
        this.notifyListeners();
    }

    /**
     * Deep merge two objects
     * @private
     */
    deepMerge(target, source) {
        // If target is null/undefined, return a copy of source
        if (target === null || target === undefined) {
            return source instanceof Object ? { ...source } : source;
        }
        
        const output = { ...target };
        
        for (const key in source) {
            if (source[key] instanceof Object) {
                output[key] = this.deepMerge(target[key], source[key]);
            } else {
                output[key] = source[key];
            }
        }
        
        return output;
    }

    /**
     * Add listener for state changes
     * @param {Function} listener - Callback to run on state change
     * @returns {Function} Cleanup function to remove listener
     */
    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    /**
     * Notify all listeners of state change
     */
    notifyListeners() {
        this.listeners.forEach(listener => listener(this.state));
    }

    /**
     * Get current project information
     * @returns {Object} Current project info
     */
    getCurrentProject() {
        return this.state.current_project;
    }

    /**
     * Update current project
     * @param {Object} project - Project data to set
     */
    setCurrentProject(project) {
        const validation = this.validateProject(project);
        
        if (!validation.isValid) {
            console.error('Invalid project data:', validation.errors);
            this.updateErrorUI(validation.errors.join('\n'));
            return false;
        }

        try {
            this.setState({
                current_project: {
                    name: project.name,
                    type: project.type,
                    metadata: project.metadata || null,
                    available_tables: project.available_tables || [],
                    uploaded_files: project.uploaded_files || [],
                    available_outputs: project.outputs || [],
                    gallery: project.gallery || []
                }
            });
            
            return true;
        } catch (error) {
            console.error('Error setting project:', error);
            this.setState({
                application: {
                    error: 'Failed to set project: ' + error.message
                }
            });
            return false;
        }
    }

    /**
     * Clear current project
     */
    clearCurrentProject() {
        this.setState({
            current_project: {
                name: null,
                type: null,
                metadata: null,
                available_tables: [],
                uploaded_files: [],
                available_outputs: [],
                gallery: []
            },
            application: {
                is_initialized: false,
                loading: false,
                error: null
            }
        });
    }

    /**
     * Initialize state from backend data
     */
    async initialize() {
        console.log('StateManager: Starting initialization');
        try {
            const context = await ApiService.fetchContext();
            console.log("StateManager: initialize", "context", context);
            
            // Update entire state to match backend structure
            this.setState({
                user: context.user,
                current_project: context.current_project,
                application: {
                    ...context.application,
                    loading: false,
                    error: null
                }
            });
            
            return context;
        } catch (error) {
            console.error('StateManager: Initialization failed:', error);
            this.setState({
                application: {
                    error: 'Initialization failed: ' + error.message,
                    loading: false
                }
            });
            throw error;
        }
    }

    /**
     * Validate project data before setting
     * @param {Object} project - Project data to validate
     * @returns {Object} Validation result
     */
    validateProject(project) {
        const errors = [];
        
        if (!project) {
            errors.push('Project data is required');
            return { isValid: false, errors };
        }
        
        if (!project.name) {
            errors.push('Project name is required');
        }
        
        if (!project.type) {
            errors.push('Project type is required');
        } else if (!this.state.application.available_project_types.includes(project.type)) {
            errors.push(`Invalid project type. Must be one of: ${this.state.application.available_project_types.join(', ')}`);
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Update UI error state
     * @param {string} errorMessage - Error message to display
     */
    updateErrorUI(errorMessage) {
        this.setState({
            application: {
                ...this.state.application,
                error: errorMessage
            }
        });
    }
}

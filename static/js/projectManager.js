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
            alert('Please select a project');
            return;
        }

        try {
            // Use ApiService to load project
            const data = await ApiService.loadProject(projectName);

            if (data.error) {
                alert(data.error);
                return;
            }

            // Get available outputs based on project type
            const outputs = this.miscManager.getAvailableOutputs(data.projectType);
            
            // Update state with project info and available outputs
            this.stateManager.setCurrentProject({
                name: data.projectName,
                type: data.projectType,
                outputs: outputs
            });
            
            // Update loading state and refresh UI elements
            this.miscManager.updateLoadingUI(false);
            window.location.reload();

            // Return success - let app.js handle UI updates
            return true;
        } catch (error) {
            console.error('loadProject: Error:', error);
            throw error; // Let app.js handle error display
        }
    }

    // Create a new project
    async createNewProject() {
        const projectName = document.getElementById('newProjectName').value;
        const projectType = document.getElementById('projectType').value;
        if (!projectName) {
            alert('Please enter a project name');
            return;
        }

        try {
            const response = await fetch('/api/projects/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ projectName, projectType })
            });
            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            // Get available outputs based on project type
            const outputs = this.miscManager.getAvailableOutputs(projectType);
            
            // Update state with project info and available outputs
            this.stateManager.setCurrentProject(projectName, projectType, outputs);
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('newProjectModal'));
            if (modal) modal.hide();

            // Refresh the page to update all UI elements
            window.location.reload();
        } catch (error) {
            console.error('createNewProject: Error:', error);
            this.miscView.showErrorMessage('Error creating project');
        }
    }

    // Add this new method
    async deleteProject(projectName) {
        if (!projectName) {
            alert('Please select a project to delete');
            return;
        }

        // Confirm deletion with user
        if (!confirm(`Are you sure you want to delete project "${projectName}"? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch('/api/projects/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    items: [{
                        type: 'project',
                        name: projectName
                    }]
                })
            });
            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            // Clear current project if it was the one deleted
            if (this.stateManager.getCurrentProject()?.name === projectName) {
                this.stateManager.clearCurrentProject();
            }

            // Refresh the page to update all UI elements
            window.location.reload();
        } catch (error) {
            console.error('deleteProject: Error:', error);
            this.stateManager.updateErrorUI('Error deleting project');
        }
    }
}
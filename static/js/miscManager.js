// This file is used to manage miscellaneous tasks that don't fit into the other managers. Supports miscView.js


import { StateManager } from './stateManager.js';
import { ApiService } from './apiService.js';

export class MiscManager {
    constructor() {
        this.stateManager = new StateManager();
        this.OUTPUT_TYPES = {
            financial: ['excel_model', 'powerpoint_overview'],
            catalyst: ['excel_overview'],
            real_estate: ['powerpoint_overview'],
            ta_grading: [],
            default: []
        };
    }   

    getAvailableOutputs(projectType) {
        return this.OUTPUT_TYPES[projectType] || this.OUTPUT_TYPES.default;
    }

    async handleDownload(projectName, outputType) {
        try {
            return await ApiService.downloadFile(projectName, outputType);
        } catch (error) {
            console.error('handleDownload error:', error);
            throw error;
        }
    }

    updateLoadingUI(isLoading) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        if (loadingSpinner) {
            loadingSpinner.style.display = isLoading ? 'block' : 'none';
        }
    }

    updateErrorUI(error) {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.textContent = error || '';
            errorContainer.style.display = error ? 'block' : 'none';
        }
    }
}
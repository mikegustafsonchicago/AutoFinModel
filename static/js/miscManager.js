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
        const outputs = this.OUTPUT_TYPES[projectType] || this.OUTPUT_TYPES.default;
        return outputs;
    }

    async handleDownload(projectName, outputType) {
        try {
            const result = await ApiService.downloadFile(projectName, outputType);
            return result;
        } catch (error) {
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
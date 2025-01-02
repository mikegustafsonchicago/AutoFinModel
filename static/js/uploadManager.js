//=============================================================
//                     FILE UPLOAD MANAGER
//=============================================================
// This module manages the business logic related to file uploads.
// It handles both PDF document uploads and gallery image uploads,
// coordinates with the server API, and manages the upload UI state.

import { ApiService } from './apiService.js';

export class UploadManager {
    constructor() {
        // Initialize any required properties
    }

    async loadExistingFiles() {
        try {
            const files = await ApiService.fetchUploadedFiles();
            
            if (files.length > 0) {
                this.view.clearTable();
                files.forEach(filename => {
                    const row = this.view.createFileRow({name: filename});
                    this.view.addRowToTable(row);
                });
            }
        } catch (error) {
            console.error('Error loading existing files');
        }
    }

    async handlePdfUpload(file, projectName) {
        try {
            if (!file) {
                throw new Error('File is required');
            }

            return await ApiService.uploadFile(file, projectName, 'uploads');
        } catch (error) {
            throw error;
        }
    }

    async deleteFile(filename, projectName) {
        try {
            if (!filename) {
                throw new Error('Filename is required');
            }

            return await ApiService.deleteFile(filename, projectName, 'uploads');
        } catch (error) {
            throw error;
        }
    }
    /**
     * Send a file to the OpenAI API for processing
     * @param {string} filename - Name of the file to process
     * @param {string} projectName - Current project name
     * @returns {Promise} - Resolves when AI processing is complete
     */
    async sendFileToAI(filename, projectName) {
        try {
            if (!filename || !projectName) {
                throw new Error('Filename and project name are required');
            }

            // Extract filename string if filename is an object
            const filenameStr = typeof filename === 'object' ? filename.name : filename;

            const payload = {
                fileName: filenameStr,
                businessDescription: '', // Can be empty for now
                userPrompt: '', // Can be empty for now
                updateScope: 'all'
            };

            return await ApiService.sendToAI(payload);

        } catch (error) {
            console.error('Error sending file to AI:', error);
            throw error;
        }
    }
}

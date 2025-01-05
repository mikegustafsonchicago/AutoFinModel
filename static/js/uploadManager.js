//=============================================================
//                     FILE UPLOAD MANAGER
//=============================================================
// This module manages the business logic related to file uploads.
// It handles both PDF document uploads and gallery image uploads,
// coordinates with the server API, and manages the upload UI state.

import { ApiService } from './apiService.js';

export class UploadManager {
    constructor(stateManager) {
        this.stateManager = stateManager;
    }

    /**
     * Get uploaded files from current project context
     * @returns {Array} List of uploaded files
     */
    getUploadedFiles() {
        const state = this.stateManager.getState();
        const files = state.current_project?.uploaded_files || {};
        
        // If it's already an object with numeric keys, return as is
        if (typeof files === 'object' && !Array.isArray(files)) {
            return files;
        }
        
        // If it's an array, convert to object with numeric keys
        if (Array.isArray(files)) {
            return files.reduce((acc, file, index) => {
                acc[index] = file;
                return acc;
            }, {});
        }
        
        return {};
    }

    /**
     * Handle PDF file upload
     * @param {File} file - File to upload
     * @param {string} projectName - Current project name
     * @param {string} projectType - Current project type
     */
    async handlePdfUpload(file, projectName, projectType) {
        try {
            if (!file || !projectName) {
                throw new Error('File and project name are required');
            }

            this.stateManager.setState({
                application: { loading: true, error: null }
            });

            const response = await ApiService.uploadFile(file, projectName, 'uploads');
            
            // Get current state
            const currentState = this.stateManager.getState();
            
            // Get existing files and ensure it's an object
            const currentFiles = currentState.current_project?.uploaded_files || {};
            
            // Convert to array if needed
            const filesArray = Array.isArray(currentFiles) ? currentFiles : Object.values(currentFiles);
            
            // Add new file
            const updatedFiles = [...filesArray, file.name];
            
            // Convert back to object format with numeric keys
            const updatedFilesObject = updatedFiles.reduce((acc, file, index) => {
                acc[index] = file;
                return acc;
            }, {});

            // Update state with new files object
            this.stateManager.setState({
                current_project: {
                    ...currentState.current_project,
                    uploaded_files: updatedFilesObject
                },
                application: { loading: false, error: null }
            });

            return response;
        } catch (error) {
            this.stateManager.setState({
                application: { 
                    loading: false, 
                    error: `Upload failed: ${error.message}` 
                }
            });
            throw error;
        }
    }

    /**
     * Delete a file from the current project
     * @param {string} filename - Name of file to delete
     * @param {string} projectName - Current project name
     */
    async deleteFile(filename, projectName) {
        try {
            if (!filename || !projectName) {
                throw new Error('Filename and project name are required');
            }

            this.stateManager.setState({
                application: { loading: true, error: null }
            });

            await ApiService.deleteFile(filename, projectName, 'uploads');

            // Get current state
            const currentState = this.stateManager.getState();

            // Convert uploaded_files object to array if needed
            const currentFiles = currentState.current_project?.uploaded_files || {};
            const filesArray = Array.isArray(currentFiles) ? currentFiles : Object.values(currentFiles);
            
            // Filter out the deleted file and remove duplicates
            const uniqueFiles = [...new Set(filesArray)].filter(f => f !== filename);
            
            // Create fresh object with sequential numeric keys
            const updatedFilesObject = uniqueFiles.reduce((acc, file, index) => {
                acc[index] = file;
                return acc;
            }, {});

            // Update state with new files object
            this.stateManager.setState({
                current_project: {
                    ...currentState.current_project,
                    uploaded_files: updatedFilesObject
                },
                application: { loading: false, error: null }
            });

            return true;
        } catch (error) {
            this.stateManager.setState({
                application: { 
                    loading: false, 
                    error: `Delete failed: ${error.message}` 
                }
            });
            throw error;
        }
    }

    /**
     * Send a file to the AI for processing
     * @param {Object|string} file - File object or filename
     * @param {HTMLTableRowElement} row - Table row for updating UI
     */
    async sendFileToAI(file, row) {
        try {
            const currentProject = this.stateManager.getCurrentProject();
            if (!currentProject?.name) {
                throw new Error('No project selected');
            }

            this.stateManager.setState({
                application: { loading: true, error: null }
            });

            const filenameStr = typeof file === 'object' ? file.name : file;
            const payload = {
                fileName: filenameStr,
                projectName: currentProject.name,
                projectType: currentProject.type,
                updateScope: 'all'
            };

            await ApiService.sendToAI(payload);

            this.stateManager.setState({
                application: { loading: false, error: null }
            });

            return true;
        } catch (error) {
            this.stateManager.setState({
                application: { 
                    loading: false, 
                    error: `AI processing failed: ${error.message}` 
                }
            });
            throw error;
        }
    }
}

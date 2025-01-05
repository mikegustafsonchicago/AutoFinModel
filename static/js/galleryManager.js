//=============================================================
//                     12. GALLERY
//=============================================================
// This module manages the gallery functionality, including removing images
// from the gallery and interfacing with the project manager.

import { ApiService } from './apiService.js';

export class GalleryManager {
    constructor(stateManager) {
        if (!stateManager) {
            throw new Error('StateManager is required');
        }
        this.stateManager = stateManager;
    }


    // Get current project from state manager
    getCurrentProject() {
        const state = this.stateManager.getState();
        const currentProject = state.current_project;
        
        console.log('GalleryManager: Getting current project from state:', currentProject);
        
        if (!currentProject || !currentProject.name) {
            throw new Error('No project selected');
        }
        
        return currentProject.name;
    }

    /**
     * Removes an image from the gallery
     * @param {string} imageName - Name of the image file to remove
     * @param {string} projectName - Name of the current project
     * @returns {Promise<void>}
     */
    async removeFromGallery(imageName, projectName) {
        try {
            console.log('Removing image from gallery:', imageName, 'project:', projectName);
            
            const result = await ApiService.deleteFile(imageName, projectName, 'gallery');
            
            // Check the response from the API
            if (result.errors) {
                console.error('Errors during deletion:', result.errors);
                throw new Error(result.errors[0]); // Throw first error message
            }

            return result;
        } catch (error) {
            console.error('Error removing image from gallery:', error);
            throw error;
        }
    }

    /**
     * Upload an image to the gallery
     * @param {File} file - The image file to upload
     * @returns {Promise<Object>} - Response with success status and filename
     */
    async uploadImage(file) {
        try {
            console.log('GalleryManager: Uploading image:', file.name);
            
            const currentProject = this.getCurrentProject();
            if (!currentProject) {
                throw new Error('No project selected');
            }

            const result = await ApiService.uploadFile(file, currentProject, 'gallery');
            return {
                success: true,
                filename: file.name
            };
        } catch (error) {
            console.error('GalleryManager: Failed to upload image:', error);
            throw error;
        }
    }

    /**
     * Internal method to handle file upload
     */
    async uploadFile(file, projectName) {
        return ApiService.uploadFile(file, projectName, 'gallery');
    }

    /**
     * Delete an image from the gallery
     */
    async deleteImage(filename) {
        try {
            const projectName = this.getCurrentProject();
            return await this.removeFromGallery(filename, projectName);
        } catch (error) {
            console.error('GalleryManager: Failed to delete image:', error);
            throw error;
        }
    }
}
// This class manages the DOM elements and interactions related to the image gallery.
// It handles uploading images, displaying them, and managing the gallery state.

//=============================================================
//                     1. INITIALIZATION
//=============================================================

import { GalleryManager } from './galleryManager.js';
import { StateManager } from './stateManager.js';
import { ApiService } from './apiService.js';

export class GalleryView {
    /**
     * Initialize the gallery view with required manager instances
     * @param {GalleryManager} galleryManager - Handles gallery business logic and state
     * @param {StateManager} stateManager - Manages application-wide state
     */
    constructor(galleryManager, stateManager) {
        // Store references to required managers
        this.galleryManager = galleryManager;
        this.stateManager = stateManager;
        
        // Bind class methods to preserve 'this' context when used as callbacks
        this.handleGalleryUpload = this.handleGalleryUpload.bind(this);
        this.initGalleryControls = this.initGalleryControls.bind(this);
        this.addImageToGallery = this.addImageToGallery.bind(this);
    }

    /**
     * Initialize the gallery view and set up all required DOM elements and event handlers
     * @returns {Promise<boolean>} Success/failure of initialization
     */
    async initialize() {
        try {
            // Get references to critical DOM elements needed for gallery functionality
            this.galleryUploadZone = document.getElementById('galleryUploadZone');
            this.galleryInput = document.getElementById('galleryImageUpload');
            this.galleryContainer = document.getElementById('imageGallery');

            // Verify all required elements exist
            if (!this.galleryUploadZone || !this.galleryInput || !this.galleryContainer) {
                throw new Error('Required gallery elements not found');
            }

            // Set up the gallery components
            this.initGalleryUpload();     // Initialize upload zone UI
            this.initGalleryControls();   // Set up event handlers for upload interactions
            await this.loadExistingGalleryImages(); // Load any existing images
            
            return true;
        } catch (error) {
            console.error('GalleryView: Initialization failed:', error);
            return false;
        }
    }

    /**
     * Set up the visual elements of the upload zone
     */
    initGalleryUpload() {
        if (!this.galleryUploadZone) return;

        // Create upload zone UI with icon and instructions
        this.galleryUploadZone.innerHTML = `
            <div class="upload-prompt">
                <i class="fas fa-images"></i>
                <p>Drop images here or click to upload</p>
            </div>
        `;
        
        this.galleryUploadZone.classList.add('upload-zone');
    }

    /**
     * Initialize drag-and-drop and click handlers for image uploads
     */
    initGalleryControls() {
        if (!this.galleryUploadZone || !this.galleryInput) return;

        // List of events we need to handle for drag and drop
        const events = ['dragenter', 'dragover', 'dragleave', 'drop'];
        
        // Prevent default browser behavior for all drag/drop events
        events.forEach(eventName => {
            this.galleryUploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        // Add visual feedback when files are dragged over the upload zone
        ['dragenter', 'dragover'].forEach(eventName => {
            this.galleryUploadZone.addEventListener(eventName, () => {
                this.galleryUploadZone.classList.add('dragover');
            }, false);
        });

        // Remove visual feedback when files leave the upload zone or are dropped
        ['dragleave', 'drop'].forEach(eventName => {
            this.galleryUploadZone.addEventListener(eventName, () => {
                this.galleryUploadZone.classList.remove('dragover');
            }, false);
        });

        // Handle file drops
        this.galleryUploadZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleGalleryUpload(files);
        }, false);

        // Handle click-to-upload functionality
        this.galleryUploadZone.addEventListener('click', () => {
            this.galleryInput.click();
        }, false);

        // Handle file selection through the file input
        this.galleryInput.addEventListener('change', (e) => {
            this.handleGalleryUpload(e.target.files);
        }, false);
    }

    /**
     * Load and display any existing gallery images from the server
     */
    async loadExistingGalleryImages() {
        if (!this.galleryContainer) {
            console.error('Gallery container element not found in DOM');
            return;
        }

        try {
            // Fetch existing images from the server
            const galleryImages = await ApiService.fetchGalleryImages();

            // Clear existing gallery content
            this.galleryContainer.innerHTML = '';
            
            // Add each image to the gallery
            galleryImages.forEach(image => {
                if (image && image.name) {
                    this.addImageToGallery(image.name);
                }
            });
        } catch (error) {
            console.error('Failed to load gallery images:', error);
        }
    }

    /**
     * Process uploaded files and add valid images to the gallery
     * @param {FileList} files - List of files to process
     */
    async handleGalleryUpload(files) {
        console.log('GalleryView: Starting gallery upload with files:', files);
        
        // Process each uploaded file
        for (const file of Array.from(files)) {
            console.log('GalleryView: Processing file:', file.name, 'type:', file.type);
            
            // Only process image files
            if (file.type.startsWith('image/')) {
                console.log('GalleryView: Valid image file detected, attempting upload');
                try {
                    const projectName = this.stateManager.currentProject;
                    const result = await this.galleryManager.uploadImage(file, projectName);
                    console.log('GalleryView: Upload result:', result);
                    
                    if (result.success) {
                        console.log('GalleryView: Upload successful, adding to gallery:', result.filename);
                        this.addImageToGallery(result.filename);
                    } else {
                        console.warn('GalleryView: Upload completed but was not successful');
                    }
                } catch (error) {
                    console.error('GalleryView: Failed to upload image:', error);
                }
            } else {
                console.warn('GalleryView: Skipping non-image file:', file.name, file.type);
            }
        }
        console.log('GalleryView: Finished processing all files');
        window.app.galleryManager.refreshGallery();
    }

    /**
     * Add a new image to the gallery display
     * @param {string} filename - Name of the image file to add
     */
    addImageToGallery(filename) {
        const imageWrapper = document.createElement('div');
        imageWrapper.className = 'gallery-image-container'; // Correct class for grid layout
    
        const img = document.createElement('img');
        const state = this.stateManager.getState();
        const username = state.user;
        const projectName = this.stateManager.currentProject;
        img.src = ApiService.getImageUrl(username, projectName, filename);
        img.alt = filename;
        img.className = 'gallery-image';
    
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'gallery-remove-btn';
        deleteBtn.innerHTML = '&times;'; // Simpler "X" symbol
        deleteBtn.onclick = async () => {
            try {
                await this.galleryManager.deleteImage(filename);
                imageWrapper.remove();
            } catch (error) {
                console.error('Failed to delete image:', error);
            }
        };
    
        imageWrapper.appendChild(img);
        imageWrapper.appendChild(deleteBtn);
        this.galleryContainer.appendChild(imageWrapper); // Appending to grid
    }
    
}

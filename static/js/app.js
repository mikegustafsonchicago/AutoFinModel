//=============================================================
//                     1. CORE APP CONFIGURATION
//=============================================================
import { ApiService } from './apiService.js';
import { StateManager } from './stateManager.js';
import { ProjectManager } from './projectManager.js';
import { TableManager } from './tableManager.js';
import { GalleryManager } from './galleryManager.js';
import { UploadManager } from './uploadManager.js';
import { ProjectView } from './projectView.js';
import { TableView } from './tableView.js';
import { GalleryView } from './galleryView.js';
import { UploadView } from './uploadView.js';
import { MiscView } from './miscView.js';
import { MiscManager } from './miscManager.js';

class App {
    constructor() {
        // Initialize managers first
        this.stateManager = new StateManager(); // Initialize stateManager
        this.miscManager = new MiscManager();
        this.projectManager = new ProjectManager(this.stateManager, this.miscManager);
        this.tableManager = new TableManager();
        this.uploadManager = new UploadManager();
        this.galleryManager = new GalleryManager(this.stateManager); // Pass stateManager to GalleryManager

        // Initialize views with their dependencies
        this.miscView = new MiscView(this.miscManager, this.stateManager);
        this.projectView = new ProjectView(this.projectManager);
        this.uploadView = new UploadView(this.uploadManager, this.stateManager);
        this.tableView = new TableView(this.tableManager);
        this.galleryView = new GalleryView(this.galleryManager, this.stateManager); // Pass stateManager to GalleryView
    }

    async initialize() {
        console.log('App: Starting initialization');
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve));
        }

        try {
            const context = await this.stateManager.initialize();
            
            if (context.current_project) {
                console.log('Initializing with project:', {
                    projectName: context.current_project,
                    projectType: context.project_info?.type
                });
                
                await this.initializeExistingSession(context);
            } else {
                console.log('No current project, initializing new session');
                await this.initializeNewSession(context);
            }
            
            console.log('App: Initialization complete');
            return true;
        } catch (error) {
            console.error('App: Initialization failed:', error);
            return false;
        }
    }

    async initializeExistingSession(initData) {
        try {
            await this.projectView.initialize();
            await this.uploadView.initialize();
            await this.galleryView.initialize();
            await this.tableView.initializeTables();
        } catch (error) {
            this.miscView.showErrorMessage('Initialization error: ' + error.message);
        }
        this.miscView.initialize(); // Add this line
    }

    async initializeNewSession(initData) {
        try {
            await this.uploadView.initialize();
        } catch (error) {
            this.miscView.showErrorMessage('Failed to initialize file upload functionality');
        }
        this.projectView.showNewProjectModal();
        await this.projectView.populateProjectsTable();
        await this.galleryView.loadExistingGalleryImages();
        this.miscView.updateProjectNameHeader();
        this.miscView.initialize();
    }
}

// Initialize app after DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing app');
    const app = new App();
    await app.initialize();
});
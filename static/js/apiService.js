export class ApiService {
    // Core API calls
    static async fetchContext() {
        try {
            const response = await fetch('/api/context');
            const data = await response.json();
            console.log('Context data:', data);
            return data;
        } catch (error) {
            console.error('Error fetching context:', error);
            throw error;
        }
    }

    static async fetchSchema(tableName) {
        try {
            console.log('Fetching schema for:', tableName);
            const response = await fetch(`/api/schema/${tableName}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Received schema:', data);
            if (data.structure && data.display) {
                return {
                    structure: data.structure,
                    display: data.display
                };
            } else {
                throw new Error('Invalid schema format received');
            }
        } catch (error) {
            console.error(`Error fetching schema for ${tableName}:`, error);
            return null;
        }
    }

    static async fetchTableData(tableName) {
        try {
            console.log('Fetching data for:', tableName);
            const response = await fetch(`/api/table_data/${tableName}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Received data:', data);
            return data.data || [];
        } catch (error) {
            console.error(`Error fetching data for ${tableName}:`, error);
            return [];
        }
    }

    static async sendToAI(payload) {
        const response = await fetch('/api/openai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                businessDescription: payload.businessDescription,
                userPrompt: payload.userPrompt,
                updateScope: payload.updateScope,
                fileName: payload.fileName
            })
        });
        if (!response.ok) throw new Error('AI processing failed');
        const data = await response.json();
        return data.text;
    }

    static async fetchUploadedFiles() {
        const context = await this.fetchContext();
        return context.uploaded_files?.filter(filename => 
            filename && filename.trim() !== ''
        ) || [];
    }

    static async uploadFile(file, project_name, destination = 'uploads') {
        console.log('ApiService: Starting file upload', {
            filename: file.name,
            project: project_name, 
            destination: destination
        });

        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_name', project_name);
        formData.append('destination', destination);

        console.log('ApiService: Sending upload request to server');
        const response = await fetch('/api/upload_file', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            console.error('ApiService: Upload failed', {
                status: response.status,
                statusText: response.statusText
            });
            throw new Error(`Upload failed: ${response.status}`);
        }
        
        console.log('ApiService: Upload successful');
        return response.json();
    }

    static async deleteFile(filename, projectName, destination = 'uploads') {
        const response = await fetch('/api/projects/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                items: [{
                    type: destination === 'gallery' ? 'gallery' : 'file',
                    name: filename,
                    projectName: projectName
                }]
            })
        });

        if (!response.ok) {
            throw new Error(`Delete failed: ${response.status}`);
        }

        return response.json();
    }

    static async fetchGalleryImages() {
        try {
            console.log('Fetching gallery images...');
            const response = await fetch('/api/gallery');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Received gallery images:', data);
            return data || [];
        } catch (error) {
            console.error('Error fetching gallery images:', error);
            return [];
        }
    }

    // Add new method for image URL construction
    static getImageUrl(username, project, filename, type = 'gallery') {
        if (!username || !project || !filename) {
            console.error('Missing required parameters for image URL:', {
                username,
                project,
                filename
            });
            throw new Error('Missing required parameters for image URL');
        }

        // If project is an object, get its name property
        const projectName = typeof project === 'object' ? project.name : project;

        console.log(`Constructing image URL for: ${filename} in ${projectName}`);
        return `/api/image/${username}/${projectName}/${type}/${filename}`;
    }

    static async loadProject(projectName) {
        try {
            const response = await fetch('/api/projects/load', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    projectName: projectName
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to load project: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error loading project:', error);
            throw error;
        }
    }

    static async downloadFile(projectName, outputType) {
        try {
            const response = await fetch(`/download_output?type=${outputType}`, {
                method: 'GET'
            });

            if (!response.ok) throw new Error('Download failed');
            
            const blob = await response.blob();
            const fileExtension = this.getFileExtension(outputType);
            return {
                blob,
                filename: `${projectName}_${outputType}.${fileExtension}`
            };
        } catch (error) {
            console.error('downloadFile error:', error);
            throw error;
        }
    }

    static getFileExtension(outputType) {
        switch(outputType) {
            case 'excel_model':
            case 'excel_overview':
                return 'xlsx';
            case 'powerpoint_overview':
                return 'pptx';
            default:
                return 'txt';
        }
    }
}

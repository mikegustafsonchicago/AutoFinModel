// This class manages the creation and data handling of dynamic tables in the application
// Handles table initialization, data processing, column generation, and formatting

import { StateManager } from './stateManager.js';
import { ApiService } from './apiService.js';

export class TableManager {
    constructor() {
        // Store table instances by their identifiers
        this.tables = {};
    }

    // Format numbers as dollar amounts with $ symbol and commas
    // Returns empty string for null/undefined values
    dollarFormatter(value) {
        // If we received a cell object, get its value
        const rawValue = typeof value?.getValue === 'function' ? value.getValue() : value;
        
        if (rawValue === null || rawValue === undefined || rawValue === '') {
            return '';
        }
        
        // Convert to number and format with $ and commas
        const numValue = parseFloat(rawValue);
        if (isNaN(numValue)) {
            return rawValue;
        }
        
        const formatted = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(numValue);

        return formatted;
    }

    /**
     * Initialize all dynamic tables based on available table structures in the project.
     * This function:
     * 1. Fetches the current context to get available table structures
     * 2. Processes each table structure file to get the base table name
     * 3. For each valid table, fetches its schema and data
     * 4. Returns configurations for all successfully processed tables
     * 
     * @returns {Promise<Array>} Array of table configurations, each containing:
     *   - tableName: String identifier for the table
     *   - schema: Table structure and display settings
     *   - data: Array of table data rows
     *   - containerId: DOM container ID for the table
     *   - tableId: Unique ID for the table element
     * @throws {Error} If there's an error fetching context or processing tables
     */
    async initializeDynamicTables() {
        try {
            // Get current application context including available table structures
            const context = await ApiService.fetchContext();
            
            // Get tables from current project
            const currentProject = context.current_project;
            if (!currentProject) {
                return [];
            }

            // Check both available_tables and tables properties
            const availableTables = currentProject.available_tables || currentProject.tables || [];
            
            if (!Array.isArray(availableTables)) {
                // If it's an object, convert to array
                availableTables = Object.keys(availableTables).map(key => availableTables[key]);
            }

            // Process structure files - remove '_structure' suffix to get base table names
            const validTables = availableTables.map(tableFile => {
                const tableName = typeof tableFile === 'string' 
                    ? tableFile.replace('_structure', '')
                    : tableFile.name || tableFile.id;
                
                return {
                    structureFile: tableFile,
                    tableName: tableName
                };
            });

            // Early return if no valid tables found
            if (!validTables.length) {
                return [];
            }

            // Process each table in parallel to get schemas and data
            const tableConfigs = await Promise.all(validTables.map(async ({tableName}) => {
                try {
                    // Fetch table schema (structure and display settings)
                    const schema = await ApiService.fetchSchema(tableName);
                    
                    if (!schema) {
                        return null;
                    }
                    
                    // Fetch actual table data
                    const data = await ApiService.fetchTableData(tableName);
                    
                    // Return complete table configuration object
                    return {
                        tableName,
                        schema,
                        data: Array.isArray(data) ? data : [], // Ensure data is an array
                        containerId: `${tableName}TableContainer`,
                        tableId: `${tableName}Table`
                    };
                } catch (error) {
                    return null;
                }
            }));
            
            // Filter out any tables that failed to load and return final configurations
            const validConfigs = tableConfigs.filter(Boolean);
            return validConfigs;
            
        } catch (error) {
            throw error;
        }
    }

    // Process table data based on schema and layout (standard or transposed)
    transposeTableData(data, schema, isTransposed) {
        if (!data || !data.length) {
            return [];
        }
        
        if (isTransposed) {
            const rootKey = Object.keys(schema.structure)[0];
            const properties = schema.structure[rootKey].items.properties;
            
            // Transform data into rows where each property becomes a row
            const transposedData = Object.entries(properties).map(([fieldName, fieldDef]) => ({
                header: fieldDef.display_name || fieldName,
                value_0: this.formatCellValue(data[0][fieldName])
            }));

            return transposedData;
        }
        
        return data;
    }

    // Generate column definitions from schema structure
    generateColumnsFromStructure(schema) {
        if (!schema || !schema.structure) {
            return { columns: [], display: {} };
        }

        const rootKey = Object.keys(schema.structure)[0];
        const properties = schema.structure[rootKey].items.properties;
        const display = schema.display || {};  // Use the display property from schema
        const isTransposed = display.defaultLayout === "transposed";

        let columns = [];

        if (isTransposed) {
            // For transposed layout, we only need two columns initially
            columns = [
                {
                    title: "Field",
                    field: "header",
                    frozen: display.frozen_column,
                    headerSort: false,
                    width: 200
                },
                {
                    title: "Value",
                    field: "value_0",
                    editor: "input",
                    headerSort: false,
                    width: 200,
                    formatter: (cell) => this.formatCellValue(cell.getValue())
                }
            ];
        } else {
            // Standard layout - generate a column for each property
            columns = Object.entries(properties)
                .sort((a, b) => (a[1].order || 999) - (b[1].order || 999))
                .map(([fieldName, fieldDef]) => {
                    // Special handling for source_object type
                    if (fieldDef.type === 'source_object') {
                        return {
                            title: fieldDef.display_name || fieldName,
                            field: fieldName,
                            formatter: (cell) => {
                                const value = cell.getValue();
                                // Handle both string and object values
                                if (typeof value === 'string') {
                                    return value;
                                }
                                // For source objects, use display_value or fall back to text_context
                                if (value && typeof value === 'object') {
                                    return value.display_value || value.text_context || 'No Source';
                                }
                                return '';
                            },
                            width: fieldDef.width || 150,
                            minWidth: fieldDef.minWidth || 100,
                            maxWidth: fieldDef.maxWidth || 400,
                            resizable: true,
                            tooltip: true
                        };
                    }
                    
                    // Default column definition for other types
                    return {
                        title: fieldDef.display_name || fieldName,
                        field: fieldName,
                        editor: fieldDef.type === 'number' ? "number" : "input",
                        formatter: this.getColumnFormatter(fieldName, fieldDef),
                        width: fieldDef.width || 150,
                        minWidth: fieldDef.minWidth || 100,
                        maxWidth: fieldDef.maxWidth || 400,
                        resizable: true,
                        tooltip: true
                    };
                });
        }

        return {
            columns,
            display: {
                isTransposed,
                allowToggle: display.allowToggle,
                frozen_column: display.frozen_column
            }
        };
    }

    // Parse source object into displayable HTML with optional link
    parseSourceObject(sourceObj) {
        if (!sourceObj) {
            return '';
        }
        
        const displayValue = sourceObj.display_value || '';
        const url = sourceObj.url || 'No source';

        // Return plain text if no URL, otherwise return clickable link
        if (url === 'No source') {
            return displayValue;
        }
        
        const html = `<a href="${url}" target="_blank">${displayValue}</a>`;
        return html;
    }

    // Load and process data for a specific table
    async loadDynamicTableData(tableIdentifier, table) {
        try {
            // Fetch table data and schema
            const responseData = await ApiService.fetchTableData(tableIdentifier);
            let tableData = responseData.data || [];
            if (!Array.isArray(tableData)) tableData = [tableData];
            
            const schema = await ApiService.fetchSchema(tableIdentifier);
            const display = schema.structure[Object.keys(schema.structure)[0]].display;
            const isTransposed = display?.defaultLayout === 'transposed';
            
            // Handle transposed table layout (rows and columns are flipped)
            if (isTransposed && tableData.length > 0) {
                const columns = [table.getColumn("header")];
                // Create dynamic columns based on data length
                tableData.forEach((_, index) => {
                    columns.push({
                        title: `Value ${index + 1}`,
                        field: `value_${index}`,
                        editor: "input",
                        formatter: (cell) => {
                            const value = cell.getValue();
                            if (value && typeof value === 'object' && value.object_type === 'source_object') {
                                return this.parseSourceObject(value);
                            }
                            return value;
                        }
                    });
                });
                table.setColumns(columns);
            }
            
            // Process and set table data
            const processedData = this.transposeTableData(tableData, schema, isTransposed);
            table.setData(processedData);
        } catch (error) {
            this.stateManager.updateErrorUI(`Error loading table data for ${tableIdentifier}`);
        }
    }

    // Add a new empty row to the table
    addRow(table) {
        const newRow = {};
        table.addRow(newRow).then(() => {
            table.redraw()
        });
    }
    
    // Helper method to update columns for transposed view
    updateTransposedColumns(table, dataLength) {
        const columns = [table.getColumn("header")];
        
        // Create a column for each data row
        for (let i = 0; i < dataLength; i++) {
            columns.push({
                title: `Value ${i + 1}`,
                field: `value_${i}`,
                editor: "input",
                headerSort: false,
                formatter: (cell) => {
                    const value = cell.getValue();
                    if (value && typeof value === 'object' && value.object_type === 'source_object') {
                        return this.parseSourceObject(value);
                    }
                    return value;
                }
            });
        }
        
        return columns;
    }

    // Helper method for consistent cell value formatting
    formatCellValue(value) {
        if (value && typeof value === 'object' && value.object_type === 'source_object') {
            return this.parseSourceObject(value);
        }
        if (typeof value === 'number') {
            return this.dollarFormatter(value);  // Pass the raw value
        }
        return value;
    }

    // Get appropriate formatter based on field properties
    getColumnFormatter(fieldName, fieldDef) {
        if (fieldDef.type === 'source_object') {
            return (cell) => this.parseSourceObject(cell.getValue());
        }
        if (fieldName.toLowerCase().includes('price') || 
            fieldName.toLowerCase().includes('value')) {
            return this.dollarFormatter;
        }
        return undefined;
    }
}
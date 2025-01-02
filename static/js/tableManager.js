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
            console.log('[dollarFormatter] Not a number, returning raw value:', rawValue);
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
        console.log('[initializeDynamicTables] Starting initialization');
        try {
            // Get current application context including available table structures
            const context = await ApiService.fetchContext();
            console.log('[initializeDynamicTables] Context received:', context); 
            
            // Ensure available_tables exists and is an array
            const availableTables = context.available_tables || [];
            console.log('[initializeDynamicTables] Available tables:', availableTables);
            
            // Process structure files - remove '_structure' suffix to get base table names
            const validTables = availableTables.map(tableFile => {
                const tableName = tableFile.replace('_structure', '');
                console.log('[initializeDynamicTables] Processing table:', tableName);
                return {
                    structureFile: tableFile,
                    tableName: tableName
                };
            });
            
            // Early return if no valid tables found
            if (!validTables.length) {
                console.log('[initializeDynamicTables] No valid tables to initialize');
                return [];
            }

            // Process each table in parallel to get schemas and data
            const tableConfigs = await Promise.all(validTables.map(async ({tableName}) => {
                console.log(`[initializeDynamicTables] Processing configuration for table: ${tableName}`);
                try {
                    // Fetch table schema (structure and display settings)
                    const schema = await ApiService.fetchSchema(tableName);
                    
                    if (!schema) {
                        console.error(`[initializeDynamicTables] No schema found for table: ${tableName}`);
                        return null;
                    }
                    
                    // Fetch actual table data
                    const data = await ApiService.fetchTableData(tableName);
                    console.log(`[initializeDynamicTables] Table ${tableName} data loaded:`, data);
                    
                    // Return complete table configuration object
                    return {
                        tableName,
                        schema,
                        data: Array.isArray(data) ? data : [], // Ensure data is an array
                        containerId: `${tableName}TableContainer`,
                        tableId: `${tableName}Table`
                    };
                } catch (error) {
                    console.error(`[initializeDynamicTables] Error processing table ${tableName}:`, error);
                    return null;
                }
            }));
            
            // Filter out any tables that failed to load and return final configurations
            const validConfigs = tableConfigs.filter(Boolean);
            console.log('[initializeDynamicTables] Final valid configurations:', validConfigs);
            return validConfigs;
            
        } catch (error) {
            console.error('[initializeDynamicTables] Error processing tables:', error);
            throw error;
        }
    }

    // Process table data based on schema and layout (standard or transposed)
    transposeTableData(data, schema, isTransposed) {
        
        if (!data || !data.length) {
            console.log('[transposeTableData] No data to process');
            return [];
        }
        
        if (isTransposed) {
            console.log('[transposeTableData] Processing transposed layout');
            const rootKey = Object.keys(schema.structure)[0];
            const properties = schema.structure[rootKey].items.properties;
            
            // Transform data into rows where each property becomes a row
            const transposedData = Object.entries(properties).map(([fieldName, fieldDef]) => ({
                header: fieldDef.display_name || fieldName,
                value_0: this.formatCellValue(data[0][fieldName])
            }));

            console.log('[transposeTableData] Transposed data:', transposedData);
            return transposedData;
        }
        
        console.log('[transposeTableData] Returning standard layout data');
        return data;
    }

    // Generate column definitions from schema structure
    generateColumnsFromStructure(schema) {
        console.log('[generateColumnsFromStructure] Starting column generation');
        
        if (!schema || !schema.structure) {
            console.error('[generateColumnsFromStructure] Invalid schema format:', schema);
            return { columns: [], display: {} };
        }

        const rootKey = Object.keys(schema.structure)[0];
        const properties = schema.structure[rootKey].items.properties;
        const display = schema.display || {};  // Use the display property from schema
        const isTransposed = display.defaultLayout === "transposed";

        console.log('[generateColumnsFromStructure] Layout type:', isTransposed ? 'transposed' : 'standard');

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
            console.log('[generateColumnsFromStructure] Generated transposed columns:', columns);
        } else {
            // Standard layout - generate a column for each property
            columns = Object.entries(properties)
                .sort((a, b) => (a[1].order || 999) - (b[1].order || 999))
                .map(([fieldName, fieldDef]) => ({
                    title: fieldDef.display_name || fieldName,
                    field: fieldName,
                    editor: fieldDef.type === 'number' ? "number" : "input",
                    formatter: this.getColumnFormatter(fieldName, fieldDef),
                    width: fieldDef.width || 150,
                    minWidth: fieldDef.minWidth || 100,
                    maxWidth: fieldDef.maxWidth || 400,
                    resizable: true
                }));
            console.log('[generateColumnsFromStructure] Generated standard columns:', columns);
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
            console.log('[parseSourceObject] Empty source object');
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
        console.log(`[loadDynamicTableData] Loading data for table ${tableIdentifier}`);
        try {
            // Fetch table data and schema
            const responseData = await ApiService.fetchTableData(tableIdentifier);
            let tableData = responseData.data || [];
            if (!Array.isArray(tableData)) tableData = [tableData];
            
            const schema = await ApiService.fetchSchema(tableIdentifier);
            const display = schema.structure[Object.keys(schema.structure)[0]].display;
            const isTransposed = display?.defaultLayout === 'transposed';
            
            console.log('[loadDynamicTableData] Table configuration', {
                tableIdentifier,
                dataLength: tableData.length,
                isTransposed
            });
            
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
                console.log('[loadDynamicTableData] Setting transposed columns:', columns);
                table.setColumns(columns);
            }
            
            // Process and set table data
            const processedData = this.transposeTableData(tableData, schema, isTransposed);
            console.log('[loadDynamicTableData] Setting processed data:', processedData);
            table.setData(processedData);
        } catch (error) {
            console.error(`[loadDynamicTableData] Error loading ${tableIdentifier}:`, error);
            this.stateManager.updateErrorUI(`Error loading table data for ${tableIdentifier}`);
        }
    }

    // Add a new empty row to the table
    addRow(table) {
        console.log('[addRow] Adding new empty row to table');
        const newRow = {};
        table.addRow(newRow).then(() => {
            console.log('[addRow] Row added successfully');
            table.redraw()
        });
    }
    
    // Helper method to update columns for transposed view
    updateTransposedColumns(table, dataLength) {
        console.log('[updateTransposedColumns] Updating columns for data length:', dataLength);
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
        
        console.log('[updateTransposedColumns] Generated columns:', columns);
        return columns;
    }

    // Helper method for consistent cell value formatting
    formatCellValue(value) {
        console.log('[formatCellValue] Formatting value:', value);
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
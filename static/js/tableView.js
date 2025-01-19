// This app manages the DOM elements related to the table view.
// It handles creating and managing dynamic tables in the UI using Tabulator library

//=============================================================
//                     1. INITIALIZATION
//=============================================================

import { TableManager } from './tableManager.js';

export class TableView {
    constructor(tableManager) {
        console.debug('[TableView] Initializing with tableManager:', tableManager);
        this.tableManager = tableManager;
        this.tables = {};
    }

    async initializeTables() {
        try {
            console.debug('[initializeTables] Starting table initialization');
            const tableConfigs = await this.tableManager.initializeDynamicTables();
            console.debug('[initializeTables] Received table configs:', tableConfigs);
            
            for (const config of tableConfigs) {
                const { tableName, schema, data, containerId, tableId } = config;
                console.debug(`[initializeTables] Processing table: ${tableName}`, {
                    schemaPresent: !!schema,
                    dataLength: data?.length,
                    containerId,
                    tableId
                });
                
                await this.createDynamicTable(
                    containerId,
                    tableId,
                    schema,
                    data,
                    this.formatTitle(tableName)
                );
            }
        } catch (error) {
            console.error('[initializeTables] Error initializing tables:', error);
        }
    }

    /**
     * Creates a dynamic table with Tabulator library
     * @param {string} containerId - ID for the container div
     * @param {string} tableId - ID for the table element
     * @param {Object} schema - Schema defining table structure and columns
     * @param {Array} data - Data to populate the table with
     * @param {string} title - Title to display above the table
     * @returns {Object} Tabulator table instance
     */
    async createDynamicTable(containerId, tableId, schema, data = [], title) {
        console.debug(`[createDynamicTable] Creating table: ${tableId}`, {
            containerId,
            schemaPresent: !!schema,
            dataLength: data?.length,
            title
        });

        title = this.formatTitle(title);
        let container = document.getElementById(containerId);
        
        if (!container) {
            console.debug(`[createDynamicTable] Container not found, creating new: ${containerId}`);
            // Create container structure if it doesn't exist
            container = document.createElement('div');
            container.id = containerId;
            container.className = 'table-container mb-4';

            const card = document.createElement('div');
            card.className = 'card';

            const header = document.createElement('div');
            header.className = 'card-header d-flex justify-content-between align-items-center';
            
            const titleElement = document.createElement('h3');
            titleElement.className = 'card-title';
            titleElement.textContent = title;
            header.appendChild(titleElement);

            const body = document.createElement('div');
            body.className = 'card-body';

            // Create table container
            const tableContainer = document.createElement('div');
            tableContainer.className = 'table-responsive';
            tableContainer.id = tableId;

            body.appendChild(tableContainer);
            card.appendChild(header);
            card.appendChild(body);
            container.appendChild(card);

            const tablesSection = document.getElementById('dynamicTables');
            if (tablesSection) {
                tablesSection.appendChild(container);
            } else {
                return null;
            }
        }

        try {
            const { columns, display } = this.tableManager.generateColumnsFromStructure(schema);
            console.debug(`[createDynamicTable] Generated columns for ${tableId}:`, {
                columnCount: columns.length,
                displaySettings: display
            });

            const processedData = this.tableManager.transposeTableData(data, schema, display.isTransposed);
            console.debug(`[createDynamicTable] Processed data for ${tableId}:`, {
                originalLength: data?.length,
                processedLength: processedData?.length,
                isTransposed: display.isTransposed
            });
            
            if (display.isTransposed) {
                console.debug(`[createDynamicTable] Creating Bootstrap table for ${tableId}`);
                return this.createBootstrapTable(tableId, processedData, display);
            } else {
                console.debug(`[createDynamicTable] Creating Tabulator table for ${tableId}`);
                return new Tabulator(`#${tableId}`, {
                    data: processedData,
                    columns: columns.map(col => ({
                        ...col,
                        tooltip: true
                    })),
                    layout: "fitDataFill",
                    height: "400px",
                    responsiveLayout: false,
                    maxHeight: "400px"
                });
            }
        } catch (error) {
            console.error(`[createDynamicTable] Failed to create table ${tableId}:`, error);
            throw error;
        }
    }

    createBootstrapTable(containerId, data, display) {
        console.debug(`[createBootstrapTable] Creating Bootstrap table for ${containerId}`, {
            dataLength: data?.length,
            displaySettings: display
        });
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('[createBootstrapTable] Container not found for Bootstrap table');
            return null;
        }

        // Create Bootstrap table
        const table = document.createElement('table');
        table.className = 'table table-striped table-hover';
        
        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        ['Field', 'Value'].forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            th.style.position = 'sticky';
            th.style.top = '0';
            th.style.backgroundColor = '#fff';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            
            // Field name cell
            const fieldCell = document.createElement('td');
            fieldCell.className = 'fw-bold';  // Bootstrap font-weight-bold
            fieldCell.style.width = '30%';
            fieldCell.textContent = row.header;
            if (display.frozen_column) {
                fieldCell.style.position = 'sticky';
                fieldCell.style.left = '0';
                fieldCell.style.backgroundColor = '#fff';
            }
            tr.appendChild(fieldCell);

            // Value cell
            const valueCell = document.createElement('td');
            valueCell.innerHTML = row.value_0;
            tr.appendChild(valueCell);

            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        // Clear container and add new table
        container.innerHTML = '';
        container.appendChild(table);

        return {
            element: table,
            setData: (newData) => {
                tbody.innerHTML = '';
                newData.forEach(row => {
                    const tr = document.createElement('tr');
                    const fieldCell = document.createElement('td');
                    fieldCell.className = 'fw-bold';
                    fieldCell.textContent = row.header;
                    tr.appendChild(fieldCell);

                    const valueCell = document.createElement('td');
                    valueCell.innerHTML = row.value_0;
                    tr.appendChild(valueCell);

                    tbody.appendChild(tr);
                });
            }
        };
    }

    /**
     * Adjusts table height based on number of rows
     * @param {Object} table - Tabulator table instance
     */
    adjustTableHeight(table) {
        const rowCount = table.getDataCount("active");
        const rowHeight = 35; // Height of each row in pixels
        const headerHeight = 40; // Height of header in pixels
        const maxHeight = 600; // Maximum allowed height
        // Calculate new height within bounds
        const newHeight = Math.min(rowCount * rowHeight + headerHeight, maxHeight);
        table.element.style.height = `${newHeight}px`;
        table.redraw();
    }

    formatTitle(tableName) {
        return tableName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}
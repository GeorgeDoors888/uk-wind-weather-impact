/**
 * Weather Impact Map Controller - Google Apps Script
 * Manipulate and control weather impact maps in Google Sheets
 * 
 * Features:
 * - Refresh map on demand
 * - Toggle map layers (DNO, GSP, Weather, Interconnectors)
 * - Adjust map zoom and center
 * - Export map as PDF
 * - Schedule automatic updates
 * - Add custom annotations
 */

// Configuration
const CONFIG = {
  SPREADSHEET_ID: '12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI',
  MAP_SHEET_NAME: 'Weather Impact Map',
  DRIVE_FOLDER_ID: null, // Set this to organize images
  PYTHON_SCRIPT_URL: null, // Set this if running Python script via webhook
};

/**
 * Create custom menu when spreadsheet opens
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('⚡ Weather Maps')
    .addItem('🔄 Refresh Map', 'refreshMap')
    .addSeparator()
    .addSubMenu(ui.createMenu('🗺️ Toggle Layers')
      .addItem('✓ Show/Hide DNOs', 'toggleDNO')
      .addItem('✓ Show/Hide GSPs', 'toggleGSP')
      .addItem('✓ Show/Hide Wind Farms', 'toggleWind')
      .addItem('✓ Show/Hide Weather', 'toggleWeather')
      .addItem('✓ Show/Hide Interconnectors', 'toggleInterconnectors'))
    .addSeparator()
    .addSubMenu(ui.createMenu('🎯 Quick Views')
      .addItem('🌍 Full Map', 'viewFull')
      .addItem('⚡ Wind Farms Only', 'viewWindOnly')
      .addItem('🔌 Interconnectors Only', 'viewInterconnectorsOnly')
      .addItem('🗺️ DNO Boundaries', 'viewDNOOnly')
      .addItem('🌦️ Weather Impact', 'viewWeatherImpact'))
    .addSeparator()
    .addItem('📊 Map Statistics', 'showStatistics')
    .addItem('📥 Export as PDF', 'exportToPDF')
    .addItem('⏰ Schedule Auto-Update', 'scheduleUpdate')
    .addItem('⚙️ Settings', 'showSettings')
    .addToUi();
  
  Logger.log('Weather Maps menu created');
}

/**
 * Refresh the map by triggering Python script
 */
function refreshMap() {
  const ui = SpreadsheetApp.getUi();
  
  // Show progress
  ui.alert('🔄 Refreshing Map', 
           'Fetching latest weather data and regenerating map...\n\n' +
           'This will take 30-60 seconds.', 
           ui.ButtonSet.OK);
  
  try {
    // Get current sheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(CONFIG.MAP_SHEET_NAME);
    
    if (!sheet) {
      throw new Error('Map sheet not found');
    }
    
    // Get current image URL
    const cell = sheet.getRange('A1');
    const formula = cell.getFormula();
    
    if (!formula || !formula.includes('IMAGE')) {
      throw new Error('No image found in A1');
    }
    
    // Add timestamp to track refresh
    const timestampSheet = getOrCreateSheet('Map Updates');
    timestampSheet.appendRow([
      new Date(),
      'Manual Refresh',
      Session.getActiveUser().getEmail()
    ]);
    
    // Note: Actual refresh requires Python script execution
    // This can be triggered via:
    // 1. Cloud Function webhook
    // 2. Apps Script URL Fetch to server running Python
    // 3. Manual run of weather_wind_impact_map.py
    
    ui.alert('✅ Refresh Initiated', 
             'Map refresh has been queued.\n\n' +
             'Run weather_wind_impact_map.py on your local machine\n' +
             'or set up a Cloud Function for automatic updates.', 
             ui.ButtonSet.OK);
    
  } catch (error) {
    ui.alert('❌ Error', 'Failed to refresh map: ' + error.message, ui.ButtonSet.OK);
    Logger.log('Refresh error: ' + error);
  }
}

/**
 * Toggle DNO layer
 */
function toggleDNO() {
  toggleLayer('show_dnos', 'DNO Boundaries');
}

/**
 * Toggle GSP layer
 */
function toggleGSP() {
  toggleLayer('show_gsps', 'GSP Boundaries');
}

/**
 * Toggle Wind Farms layer
 */
function toggleWind() {
  toggleLayer('show_wind', 'Wind Farms');
}

/**
 * Toggle Weather layer
 */
function toggleWeather() {
  toggleLayer('show_weather_fronts', 'Weather Fronts');
}

/**
 * Toggle Interconnectors layer
 */
function toggleInterconnectors() {
  toggleLayer('show_interconnectors', 'Interconnectors');
}

/**
 * Generic layer toggle function
 */
function toggleLayer(configKey, layerName) {
  const ui = SpreadsheetApp.getUi();
  
  // Get or create config sheet
  const configSheet = getOrCreateSheet('Map Config');
  
  // Find or create config row
  const data = configSheet.getDataRange().getValues();
  let rowIndex = -1;
  
  for (let i = 0; i < data.length; i++) {
    if (data[i][0] === configKey) {
      rowIndex = i + 1;
      break;
    }
  }
  
  if (rowIndex === -1) {
    // Create new row
    configSheet.appendRow([configKey, true]);
    rowIndex = configSheet.getLastRow();
  }
  
  // Toggle value
  const currentValue = configSheet.getRange(rowIndex, 2).getValue();
  const newValue = !currentValue;
  configSheet.getRange(rowIndex, 2).setValue(newValue);
  
  ui.alert('🎨 Layer Toggled', 
           layerName + ' is now: ' + (newValue ? '✓ VISIBLE' : '✗ HIDDEN') + '\n\n' +
           'Run "Refresh Map" to apply changes.', 
           ui.ButtonSet.OK);
}

/**
 * Show full map view
 */
function viewFull() {
  setQuickView('full', 'All layers enabled');
}

/**
 * Show wind farms only
 */
function viewWindOnly() {
  setQuickView('wind_only', 'Wind farms with weather impacts');
}

/**
 * Show interconnectors only
 */
function viewInterconnectorsOnly() {
  setQuickView('interconnectors_only', 'Power interconnectors');
}

/**
 * Show DNO boundaries only
 */
function viewDNOOnly() {
  setQuickView('dno_only', 'DNO boundaries');
}

/**
 * Show weather impact view
 */
function viewWeatherImpact() {
  setQuickView('weather_impact', 'Wind farms + weather + interconnectors');
}

/**
 * Set quick view configuration
 */
function setQuickView(viewType, description) {
  const ui = SpreadsheetApp.getUi();
  const configSheet = getOrCreateSheet('Map Config');
  
  // Clear existing config
  configSheet.clear();
  configSheet.appendRow(['Setting', 'Value']);
  
  // Set view type
  configSheet.appendRow(['view_type', viewType]);
  
  // Set layer visibility based on view type
  const configs = {
    'full': {
      show_dnos: true,
      show_gsps: false,
      show_wind: true,
      show_weather_fronts: true,
      show_weather_impacts: true,
      show_interconnectors: true
    },
    'wind_only': {
      show_dnos: false,
      show_gsps: false,
      show_wind: true,
      show_weather_fronts: true,
      show_weather_impacts: true,
      show_interconnectors: false
    },
    'interconnectors_only': {
      show_dnos: false,
      show_gsps: false,
      show_wind: false,
      show_weather_fronts: false,
      show_weather_impacts: false,
      show_interconnectors: true
    },
    'dno_only': {
      show_dnos: true,
      show_gsps: false,
      show_wind: false,
      show_weather_fronts: false,
      show_weather_impacts: false,
      show_interconnectors: false
    },
    'weather_impact': {
      show_dnos: true,
      show_gsps: false,
      show_wind: true,
      show_weather_fronts: true,
      show_weather_impacts: true,
      show_interconnectors: true
    }
  };
  
  const config = configs[viewType];
  for (const [key, value] of Object.entries(config)) {
    configSheet.appendRow([key, value]);
  }
  
  ui.alert('🎯 View Changed', 
           'Quick view set to: ' + description + '\n\n' +
           'Run "Refresh Map" to apply changes.', 
           ui.ButtonSet.OK);
}

/**
 * Show map statistics
 */
function showStatistics() {
  const ui = SpreadsheetApp.getUi();
  
  // This would ideally fetch data from the Python script output
  // For now, show static info
  
  const stats = `
📊 UK WEATHER IMPACT MAP STATISTICS

🏭 Wind Farms: 15 offshore wind farms
⚡ Total Capacity: 11.57 GW
🔌 Interconnectors: 12 power links
📍 DNO Regions: 14 distribution areas
🗺️ GSP Points: 100 grid supply points

🌦️ Weather Data: Live from Open-Meteo
📡 Update Frequency: On-demand
🎨 Resolution: 7680×7680 pixels
💾 Display Size: 1400×1400 pixels

Last Update: Check "Map Updates" sheet
  `;
  
  ui.alert('📊 Map Statistics', stats, ui.ButtonSet.OK);
}

/**
 * Export map as PDF
 */
function exportToPDF() {
  const ui = SpreadsheetApp.getUi();
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(CONFIG.MAP_SHEET_NAME);
    
    if (!sheet) {
      throw new Error('Map sheet not found');
    }
    
    // Create PDF blob
    const pdfBlob = ss.getAs('application/pdf');
    pdfBlob.setName('Weather_Impact_Map_' + Utilities.formatDate(new Date(), 'GMT', 'yyyy-MM-dd_HHmm') + '.pdf');
    
    // Save to Drive
    const folder = CONFIG.DRIVE_FOLDER_ID ? 
      DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID) : 
      DriveApp.getRootFolder();
    
    const file = folder.createFile(pdfBlob);
    
    ui.alert('📥 PDF Exported', 
             'Map exported successfully!\n\n' +
             'File: ' + file.getName() + '\n' +
             'Location: ' + folder.getName() + '\n\n' +
             'Open: ' + file.getUrl(), 
             ui.ButtonSet.OK);
    
  } catch (error) {
    ui.alert('❌ Export Failed', 'Error: ' + error.message, ui.ButtonSet.OK);
    Logger.log('PDF export error: ' + error);
  }
}

/**
 * Schedule automatic updates
 */
function scheduleUpdate() {
  const ui = SpreadsheetApp.getUi();
  
  const response = ui.alert(
    '⏰ Schedule Auto-Update',
    'Would you like to enable automatic map updates?\n\n' +
    'Options:\n' +
    '• Every hour: Hourly weather updates\n' +
    '• Every 6 hours: 4x daily updates\n' +
    '• Daily at 8am: Once per day\n\n' +
    'Note: Requires Python script to run on schedule',
    ui.ButtonSet.YES_NO
  );
  
  if (response === ui.Button.YES) {
    // Create time-based trigger
    const trigger = ScriptApp.newTrigger('refreshMap')
      .timeBased()
      .everyHours(6) // Update every 6 hours
      .create();
    
    ui.alert('✅ Schedule Created', 
             'Auto-update enabled!\n\n' +
             'Frequency: Every 6 hours\n' +
             'Trigger ID: ' + trigger.getUniqueId() + '\n\n' +
             'To disable: Go to Extensions → Apps Script → Triggers', 
             ui.ButtonSet.OK);
  }
}

/**
 * Show settings dialog
 */
function showSettings() {
  const ui = SpreadsheetApp.getUi();
  
  const settings = `
⚙️ WEATHER MAP SETTINGS

Current Configuration:
• Spreadsheet: ${CONFIG.SPREADSHEET_ID}
• Map Sheet: ${CONFIG.MAP_SHEET_NAME}
• Display Size: 1400×1400 pixels
• Image Mode: Fit with aspect ratio

Available Actions:
1. Change map center coordinates
2. Adjust zoom level
3. Set custom display size
4. Configure Drive folder
5. Set webhook URL

To modify settings:
1. Go to Extensions → Apps Script
2. Edit CONFIG object at top of script
3. Save and refresh

For advanced customization:
See weather_wind_impact_map.py MAP_CONFIG
  `;
  
  ui.alert('⚙️ Settings', settings, ui.ButtonSet.OK);
}

/**
 * Resize map display
 */
function resizeMapDisplay(width, height) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.MAP_SHEET_NAME);
  
  if (!sheet) {
    throw new Error('Map sheet not found');
  }
  
  const sheetId = sheet.getSheetId();
  
  // Resize column A
  const requests = [{
    updateDimensionProperties: {
      range: {
        sheetId: sheetId,
        dimension: 'COLUMNS',
        startIndex: 0,
        endIndex: 1
      },
      properties: {
        pixelSize: width
      },
      fields: 'pixelSize'
    }
  }];
  
  // Resize rows to match height
  const rowHeight = Math.ceil(height / 30);
  requests.push({
    updateDimensionProperties: {
      range: {
        sheetId: sheetId,
        dimension: 'ROWS',
        startIndex: 0,
        endIndex: 30
      },
      properties: {
        pixelSize: rowHeight
      },
      fields: 'pixelSize'
    }
  });
  
  Sheets.Spreadsheets.batchUpdate({requests: requests}, ss.getId());
}

/**
 * Get or create a sheet by name
 */
function getOrCreateSheet(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    
    // Format header row
    if (sheetName === 'Map Updates') {
      sheet.appendRow(['Timestamp', 'Action', 'User']);
      sheet.getRange('A1:C1').setFontWeight('bold');
    } else if (sheetName === 'Map Config') {
      sheet.appendRow(['Setting', 'Value']);
      sheet.getRange('A1:B1').setFontWeight('bold');
    }
  }
  
  return sheet;
}

/**
 * Add custom annotation to map
 */
function addAnnotation() {
  const ui = SpreadsheetApp.getUi();
  
  const result = ui.prompt(
    '📝 Add Annotation',
    'Enter annotation text:',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (result.getSelectedButton() === ui.Button.OK) {
    const text = result.getResponseText();
    const sheet = getOrCreateSheet('Map Annotations');
    sheet.appendRow([new Date(), text, Session.getActiveUser().getEmail()]);
    
    ui.alert('✅ Annotation Added', 'Your note has been saved.', ui.ButtonSet.OK);
  }
}

/**
 * Get map configuration from sheet
 */
function getMapConfig() {
  const configSheet = getOrCreateSheet('Map Config');
  const data = configSheet.getDataRange().getValues();
  
  const config = {};
  for (let i = 1; i < data.length; i++) { // Skip header
    config[data[i][0]] = data[i][1];
  }
  
  return config;
}

/**
 * Test function - check if everything works
 */
function testSetup() {
  const ui = SpreadsheetApp.getUi();
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(CONFIG.MAP_SHEET_NAME);
    
    if (!sheet) {
      throw new Error('Map sheet not found');
    }
    
    const cell = sheet.getRange('A1');
    const formula = cell.getFormula();
    
    const hasImage = formula && formula.includes('IMAGE');
    
    ui.alert('🧪 Setup Test', 
             'Test Results:\n\n' +
             '✓ Spreadsheet ID: ' + ss.getId() + '\n' +
             '✓ Map Sheet: ' + (sheet ? 'Found' : 'NOT FOUND') + '\n' +
             '✓ Image Formula: ' + (hasImage ? 'Found' : 'NOT FOUND') + '\n\n' +
             (hasImage ? '✅ Everything looks good!' : '⚠️ Map needs to be generated'), 
             ui.ButtonSet.OK);
    
  } catch (error) {
    ui.alert('❌ Test Failed', 'Error: ' + error.message, ui.ButtonSet.OK);
  }
}

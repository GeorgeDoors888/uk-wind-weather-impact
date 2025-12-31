# Weather Map Controller - Apps Script Guide

## Overview

**File:** `WEATHER_MAP_CONTROLLER.gs`

This Google Apps Script adds interactive controls to manipulate weather impact maps directly within Google Sheets. No need to run Python scripts manually - control everything from a custom menu!

## 🚀 Installation

### 1. Open Apps Script Editor

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI
2. Click **Extensions** → **Apps Script**
3. Delete any existing code in `Code.gs`

### 2. Add the Script

1. Copy all content from `WEATHER_MAP_CONTROLLER.gs`
2. Paste into the Apps Script editor
3. Click **💾 Save** (or Ctrl+S / Cmd+S)
4. Name the project: "Weather Map Controller"

### 3. First Run

1. Close the Apps Script tab
2. Refresh your Google Sheet
3. You'll see a new menu: **⚡ Weather Maps**
4. Click it to see all options!

## 📋 Features

### Custom Menu

When you open the sheet, a new menu appears with these options:

```
⚡ Weather Maps
├── 🔄 Refresh Map
├── ─────────────
├── 🗺️ Toggle Layers
│   ├── ✓ Show/Hide DNOs
│   ├── ✓ Show/Hide GSPs
│   ├── ✓ Show/Hide Wind Farms
│   ├── ✓ Show/Hide Weather
│   └── ✓ Show/Hide Interconnectors
├── ─────────────
├── 🎯 Quick Views
│   ├── 🌍 Full Map
│   ├── ⚡ Wind Farms Only
│   ├── 🔌 Interconnectors Only
│   ├── 🗺️ DNO Boundaries
│   └── 🌦️ Weather Impact
├── ─────────────
├── 📊 Map Statistics
├── 📥 Export as PDF
├── ⏰ Schedule Auto-Update
└── ⚙️ Settings
```

## 🎮 How to Use

### Refresh Map

**Menu:** ⚡ Weather Maps → 🔄 Refresh Map

Updates the map with latest weather data. This logs the refresh request but requires running the Python script to actually generate a new map:

```bash
python weather_wind_impact_map.py
```

The script will read the `Map Config` sheet to apply your layer preferences.

### Toggle Layers

**Menu:** ⚡ Weather Maps → 🗺️ Toggle Layers → [Choose Layer]

Turn individual map layers on/off:

- **DNOs:** 14 distribution network regions
- **GSPs:** 100 grid supply points  
- **Wind Farms:** 15 offshore wind farms
- **Weather:** Weather fronts, pressure systems
- **Interconnectors:** 12 power cables to Europe

**How it works:**
1. Click to toggle a layer
2. Setting is saved to "Map Config" sheet
3. Click "Refresh Map" to apply changes
4. Run Python script to regenerate

### Quick Views

**Menu:** ⚡ Weather Maps → 🎯 Quick Views → [Choose View]

Instantly switch between preset map configurations:

#### 🌍 Full Map
Shows everything: DNOs, wind farms, weather, interconnectors

#### ⚡ Wind Farms Only
Focus on wind farms with weather impacts

#### 🔌 Interconnectors Only
View just the power interconnectors

#### 🗺️ DNO Boundaries
Show only DNO regions

#### 🌦️ Weather Impact
Wind farms + weather + interconnectors (optimal for operations)

### Map Statistics

**Menu:** ⚡ Weather Maps → 📊 Map Statistics

Displays summary information:
- 15 offshore wind farms (11.57 GW)
- 12 interconnectors
- 14 DNO regions
- 100 GSP points
- Map resolution and update info

### Export as PDF

**Menu:** ⚡ Weather Maps → 📥 Export as PDF

Exports the current map view as a PDF file:
- Saves to Google Drive
- Filename includes timestamp
- Can set custom Drive folder in CONFIG

### Schedule Auto-Update

**Menu:** ⚡ Weather Maps → ⏰ Schedule Auto-Update

Creates a time-based trigger to refresh the map automatically:
- Default: Every 6 hours
- Can customize in the code
- Requires Python script automation (see below)

### Settings

**Menu:** ⚡ Weather Maps → ⚙️ Settings

Shows current configuration and how to modify settings.

## 🔧 Configuration

Edit the `CONFIG` object at the top of the script:

```javascript
const CONFIG = {
  SPREADSHEET_ID: '12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI',
  MAP_SHEET_NAME: 'Weather Impact Map',
  DRIVE_FOLDER_ID: null, // Set to organize exported PDFs
  PYTHON_SCRIPT_URL: null, // Set for webhook automation
};
```

### Setting Drive Folder

To organize exported PDFs:

1. Create a folder in Google Drive
2. Right-click → Get link
3. Extract folder ID from URL: `folders/[FOLDER_ID]`
4. Set in CONFIG: `DRIVE_FOLDER_ID: 'your-folder-id'`

## 📊 Created Sheets

The script automatically creates helper sheets:

### Map Config
Stores layer toggle settings:

| Setting | Value |
|---------|-------|
| show_dnos | TRUE |
| show_gsps | FALSE |
| show_wind | TRUE |
| show_weather_fronts | TRUE |
| show_interconnectors | TRUE |

### Map Updates
Tracks refresh history:

| Timestamp | Action | User |
|-----------|--------|------|
| 2025-12-31 10:30 | Manual Refresh | user@example.com |

### Map Annotations
Optional notes/annotations:

| Timestamp | Annotation | User |
|-----------|------------|------|
| 2025-12-31 10:35 | High winds expected | user@example.com |

## 🤖 Python Integration

To fully automate map updates, integrate with the Python script:

### Option 1: Manual (Current)

1. Click "Refresh Map" in Sheets
2. Run Python script manually:
   ```bash
   python weather_wind_impact_map.py
   ```
3. Script reads `Map Config` sheet
4. Generates map with selected layers
5. Uploads to Sheets

### Option 2: Webhook (Advanced)

Set up a Cloud Function or server endpoint:

```python
# Flask example
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/refresh-map', methods=['POST'])
def refresh_map():
    # Read config from Sheets
    config = read_sheet_config()
    
    # Run Python script with config
    subprocess.run(['python', 'weather_wind_impact_map.py'])
    
    return {'status': 'success'}
```

Then set in CONFIG:
```javascript
PYTHON_SCRIPT_URL: 'https://your-server.com/refresh-map'
```

### Option 3: Apps Script Triggers + Automated Python

1. Set up Cloud Scheduler to run Python script every 6 hours
2. Python script reads `Map Config` sheet automatically
3. Apps Script triggers update the config
4. System stays in sync

## 🎨 Customization

### Add Custom Views

Edit the `setQuickView()` function:

```javascript
const configs = {
  'my_custom_view': {
    show_dnos: true,
    show_gsps: true,
    show_wind: true,
    show_weather_fronts: false,
    show_weather_impacts: false,
    show_interconnectors: false
  }
};
```

Then add menu item:
```javascript
.addItem('🎯 My Custom View', 'viewMyCustom')
```

### Change Update Frequency

In `scheduleUpdate()`:

```javascript
// Current: Every 6 hours
.everyHours(6)

// Options:
.everyHours(1)     // Hourly
.everyDays(1)      // Daily
.atHour(8)         // Daily at 8am
.everyMinutes(30)  // Every 30 min
```

### Modify Display Size

Call `resizeMapDisplay()`:

```javascript
resizeMapDisplay(1920, 1080); // Width, Height in pixels
```

Or add to menu:
```javascript
.addItem('📐 Resize: 1920×1080', 'resize1920x1080')

function resize1920x1080() {
  resizeMapDisplay(1920, 1080);
}
```

## 🧪 Testing

Run the test function to verify setup:

1. In Apps Script editor, select `testSetup` from function dropdown
2. Click **Run** (▶️ button)
3. Review results in popup

## 📱 Mobile Access

The custom menu works on mobile:
1. Open Google Sheets app
2. Tap ⋮ (three dots)
3. Scroll to "⚡ Weather Maps"
4. Select action

## 🔐 Permissions

First time you run a function, Google will ask for permissions:

**Required:**
- ✓ View and manage spreadsheets
- ✓ Connect to external services (for webhook)
- ✓ Create time-based triggers (for scheduling)

Click "Advanced" → "Go to Weather Map Controller" → "Allow"

## 🐛 Troubleshooting

### Menu not appearing?
- Refresh the sheet (Ctrl+R / Cmd+R)
- Check: Extensions → Apps Script → Code is saved
- Run `onOpen()` manually in Apps Script

### "Map sheet not found" error?
- Check `CONFIG.MAP_SHEET_NAME` matches your sheet tab name
- Default: "Weather Impact Map"

### PDF export fails?
- Check: Do you have edit permissions on the Sheet?
- Try setting a specific `DRIVE_FOLDER_ID`

### Layer toggles not working?
- Check "Map Config" sheet was created
- Settings are saved but require Python script re-run

## 📖 Function Reference

### Core Functions

| Function | Purpose |
|----------|---------|
| `onOpen()` | Creates custom menu |
| `refreshMap()` | Triggers map update |
| `toggleLayer()` | Toggle specific layer on/off |
| `setQuickView()` | Apply preset view configuration |
| `showStatistics()` | Display map stats |
| `exportToPDF()` | Export to PDF file |
| `scheduleUpdate()` | Create time-based trigger |
| `getMapConfig()` | Read config from sheet |
| `resizeMapDisplay()` | Change display dimensions |

### Helper Functions

| Function | Purpose |
|----------|---------|
| `getOrCreateSheet()` | Get/create helper sheets |
| `addAnnotation()` | Add custom note |
| `testSetup()` | Verify configuration |

## 🎯 Workflow Example

1. **Open Sheet** → Custom menu appears
2. **Click:** 🎯 Quick Views → 🔌 Interconnectors Only
3. **Click:** 🔄 Refresh Map
4. **Run on terminal:** `python weather_wind_impact_map.py`
5. **Result:** Map shows only interconnectors
6. **Click:** 📥 Export as PDF → Save to Drive
7. **Done!** PDF ready for presentation

## 📚 Additional Resources

- **Python Script:** `weather_wind_impact_map.py`
- **Map Config:** Edit MAP_CONFIG dictionary in Python
- **Sheet Optimization:** See `SHEETS_IMAGE_OPTIMIZATION.md`
- **Interconnectors:** See `INTERCONNECTORS_GUIDE.md`

## 💡 Pro Tips

1. **Create favorites:** Add most-used views to menu
2. **Schedule updates:** Run during off-peak hours (3am)
3. **Annotate changes:** Use Map Annotations sheet for notes
4. **Track history:** Check Map Updates sheet for audit trail
5. **Export regularly:** Keep PDF archive of key dates

---

**Created:** 2025-12-31  
**Version:** 1.0  
**Compatible with:** weather_wind_impact_map.py v2.0+

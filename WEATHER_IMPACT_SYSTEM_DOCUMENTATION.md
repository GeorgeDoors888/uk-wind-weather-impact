# UK Offshore Wind Farm Weather Impact Forecasting System

## 📋 Overview

A comprehensive automated system that monitors real-time weather conditions, forecasts operational impacts, and visualizes weather fronts affecting UK offshore wind farms. The system integrates live meteorological data with wind farm operational parameters to predict generation capacity, detect weather-related issues, and present findings in professional, newspaper-style weather maps.

**Live Dashboard:** [Google Sheets - Weather Impact Map](https://docs.google.com/spreadsheets/d/12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI)

---

## 🎯 Key Features

### 1. Real-Time Weather Monitoring
- **Data Source:** Open-Meteo API (free, no API key required)
- **Coverage:** 15 major UK offshore wind farms
- **Metrics Tracked:**
  - Wind speed (m/s) and direction (degrees)
  - Wind gusts (m/s)
  - Temperature (°C) and feels-like temperature
  - Humidity (%)
  - Atmospheric pressure (hPa)
  - Cloud cover (%)
  - Precipitation (mm)
  - Weather conditions (clear, cloudy, rain, snow, etc.)

### 2. Operational Impact Analysis
The system analyzes weather data against wind turbine operational thresholds:

#### **Cut-In Speed:** 3.5 m/s
- Below this speed: No power generation
- Status: IDLE (Yellow marker)

#### **Rated Speed:** 12.5 m/s
- Optimal generation at nameplate capacity
- Status: NORMAL (Green marker)

#### **Cut-Out Speed:** 25.0 m/s
- Emergency shutdown to protect turbines
- Status: SHUTDOWN (Red marker)

#### **Icing Risk Detection**
- Temperature ≤ 0°C + Humidity ≥ 80%
- Ice buildup affects blade aerodynamics
- Status: ICING RISK (Orange marker)

### 3. 12-Hour Weather Forecasting
- Hourly predictions for next 12 hours
- Impact timeline with ETA (hours)
- Duration estimates for weather events
- Automated event detection:
  - High wind shutdown events
  - Low wind idle periods
  - Icing risk windows
  - Sub-optimal generation periods

### 4. Weather Front Tracking
Professional meteorological visualization using newspaper-style symbols:

#### **Pressure Systems**
- **H** (Red) - High pressure centers (>1015 hPa)
- **L** (Blue) - Low pressure centers (<1010 hPa)

#### **Weather Fronts**
- **▼** (Blue) - Cold fronts (temperature dropping)
- **▲** (Red) - Warm fronts (temperature rising)
- Front detection via temperature gradients

#### **Wind Patterns**
- **↑ → ↓ ←** - Cardinal wind direction arrows
- Wind speed displayed with each arrow
- Current conditions at grid points

#### **Weather Symbols**
- **☀** - Clear sky
- **☁** - Cloudy
- **🌧** - Rain
- **❄** - Snow
- **⛈** - Thunderstorm
- **🌫** - Fog

### 5. Interactive Map Features
- **Color-Coded Wind Farms:**
  - 🟢 Green: Normal operation (>80% capacity)
  - 🟡 Yellow: Sub-optimal wind (<80% capacity)
  - 🟠 Orange: Icing risk (temp <0°C + high humidity)
  - 🔴 Red: Emergency shutdown (wind >25 m/s)

- **Detailed Popups:** Click any wind farm marker to see:
  - Current operational status
  - Real-time power output (MW)
  - Capacity factor (%)
  - Current weather conditions
  - Upcoming weather events with ETA
  - Sea state conditions (wave height, period)

- **DNO Boundary Overlay:** Shows UK Distribution Network Operator regions
- **GSP Boundary Overlay:** Grid Supply Point areas (optional)

### 6. Automated Google Sheets Integration
- High-resolution map images (7680x7680 pixels)
- Automatic upload to Google Drive
- Insert into Google Sheets via =IMAGE() formula
- Updates on demand by running Python script
- OAuth 2.0 authentication (no service account limits)

---

## 🏭 Wind Farm Fleet

The system monitors 15 major UK offshore wind farms with total capacity of **11.57 GW**:

| Wind Farm | Capacity (MW) | Turbines | Owner | Status | Location |
|-----------|---------------|----------|-------|--------|----------|
| **Hornsea Two** | 1,386 | 165 | Ørsted | Operational | East Coast |
| **Hornsea One** | 1,218 | 174 | Ørsted | Operational | East Coast |
| **Dogger Bank A** | 1,200 | 90 | SSE Renewables | Under Construction | North Sea |
| **Dogger Bank B** | 1,200 | 90 | SSE Renewables | Under Construction | North Sea |
| **Moray East** | 950 | 100 | Ocean Winds | Operational | Scotland |
| **Triton Knoll** | 857 | 90 | RWE | Operational | East Coast |
| **East Anglia One** | 714 | 102 | ScottishPower | Operational | East Anglia |
| **Walney Extension** | 659 | 87 | Ørsted | Operational | Irish Sea |
| **London Array** | 630 | 175 | Ørsted | Operational | Thames Estuary |
| **Beatrice** | 588 | 84 | SSE Renewables | Operational | Scotland |
| **Gwynt y Môr** | 576 | 160 | RWE | Operational | North Wales |
| **Greater Gabbard** | 504 | 140 | SSE Renewables | Operational | East Anglia |
| **Rampion** | 400 | 116 | RWE | Operational | South Coast |
| **West of Duddon Sands** | 389 | 108 | Ørsted | Operational | Irish Sea |
| **Thanet** | 300 | 100 | Vattenfall | Operational | Kent |

---

## 📊 Current Fleet Status (Last Run)

**Total Capacity:** 11.57 GW  
**Current Output:** 2.19 GW (19% capacity factor)  
**Weather Conditions:** Moderate winds (4-10 m/s), all farms sub-optimal

**Fleet Breakdown:**
- 🟢 Normal: 0 farms
- 🟡 Sub-optimal: 15 farms
- 🟠 Icing Risk: 0 farms
- 🔴 Shutdown: 0 farms

---

## 🛠️ Technical Architecture

### Python Scripts

#### 1. **weather_fetcher.py**
Core weather data retrieval module.

**Functions:**
- `get_current_weather(lat, lon)` - Fetch current conditions
- `get_hourly_forecast(lat, lon, hours)` - Get hourly forecasts
- `get_marine_forecast(lat, lon, hours)` - Marine data (waves, swell)
- `get_wind_farm_weather(wind_farm, ...)` - Complete weather package for a farm
- `fetch_all_wind_farms(geojson_path, ...)` - Batch fetch for all farms
- `get_bigquery_wind_generation(hours_back)` - Historical generation data

**Data Sources:**
- Open-Meteo Forecast API: https://api.open-meteo.com/v1/forecast
- Open-Meteo Marine API: https://marine-api.open-meteo.com/v1/marine
- BigQuery: `inner-cinema-476211-u9.uk_energy_prod` dataset

#### 2. **wind_impact_analyzer.py**
Operational impact analysis engine.

**Classes:**
- `WindImpactAnalyzer` - Main analysis class

**Key Methods:**
- `analyze_current_conditions(weather)` - Assess current operational status
- `analyze_forecast(forecast, current_time)` - Detect upcoming events
- `get_overall_status(current_status, events)` - Priority determination
- `format_impact_summary(wind_farm, analysis)` - Human-readable output

**Thresholds:**
```python
CUT_IN_SPEED = 3.5 m/s
RATED_SPEED = 12.5 m/s
CUT_OUT_SPEED = 25.0 m/s
ICING_TEMP = 0.0°C
ICING_HUMIDITY = 80%
```

#### 3. **weather_front_tracker.py**
Meteorological front detection and visualization.

**Classes:**
- `WeatherFrontTracker` - Front detection system

**Key Methods:**
- `get_grid_weather(bounds, grid_size)` - Fetch weather grid
- `detect_pressure_systems(grid_data)` - Find highs/lows
- `detect_fronts(grid_data)` - Identify cold/warm fronts
- `calculate_front_velocity(grid_data)` - Front movement speed
- `get_wind_arrow(direction_deg)` - Unicode arrow selection
- `get_weather_symbol(weather_code)` - WMO code to emoji
- `add_fronts_to_map(folium_map, ...)` - Render on map

**Detection Algorithms:**
- Pressure systems: Local extrema detection (maxima/minima)
- Weather fronts: Temperature gradient analysis (>1.5°C per degree lat/lon)
- Front velocity: Wind speed × 0.5 (fronts move ~50% of wind speed)

#### 4. **weather_wind_impact_map.py** (MAIN SCRIPT)
Master orchestration and map generation.

**Functions:**
- `get_oauth_credentials()` - Google API authentication
- `generate_weather_impact_map()` - Create Folium interactive map
- `capture_screenshot(html_file)` - Selenium high-res screenshot
- `upload_to_drive_oauth(file_path, creds)` - Upload to Drive
- `insert_image_in_sheet(image_url, creds)` - Insert into Sheets

**Configuration:**
```python
MAP_CONFIG = {
    'show_dnos': True,
    'show_gsps': False,
    'show_wind': True,
    'show_weather_impacts': True,
    'show_weather_fronts': True,
    'center': [54.5, -2.5],
    'zoom': 6.5
}
```

**Dependencies:**
- `folium` - Interactive web mapping
- `selenium` - Browser automation for screenshots
- `webdriver_manager` - ChromeDriver management
- `google-auth-oauthlib` - OAuth 2.0 authentication
- `googleapiclient` - Google Drive/Sheets APIs
- `Pillow` - Image processing
- `requests` - HTTP client
- `numpy` - Numerical operations

### Data Files

#### GeoJSON Exports
- **offshore_wind_farms.geojson** (647 B)
  - 15 wind farm point features
  - Properties: name, capacity_mw, turbine_count, owner, status, commissioned_year

- **dno_boundaries.geojson** (5.6 MB)
  - 14 DNO boundary polygons
  - Properties: dno_code, dno_full_name, area_km2

- **gsp_boundaries.geojson** (9.98 MB)
  - 100 GSP boundary polygons
  - Properties: gsp_id, gsp_name, gsp_group

#### Authentication Files
- **oauth_credentials.json** - OAuth 2.0 client secrets (Desktop app)
- **oauth_token.pickle** - Cached authentication token
- **thesis-harvester-key.json** - Service account credentials (deprecated)

#### Output Files
- **weather_impact_map.html** - Interactive Folium map
- **weather_impact_map.png** - High-resolution screenshot (7680×7680)
- **wind_farm_weather_YYYYMMDD_HHMMSS.json** - Raw weather data export

---

## 🚀 Usage Instructions

### Quick Start
```bash
cd "/Users/georgemajor/Jibber Jabber Al knowing Dent"
source .venv/bin/activate
python weather_wind_impact_map.py
```

### First-Time Setup

1. **Install Dependencies:**
```bash
pip install folium selenium webdriver-manager google-auth-oauthlib google-api-python-client Pillow requests numpy google-cloud-bigquery
```

2. **Configure OAuth 2.0:**
   - Place `oauth_credentials.json` in working directory
   - First run will open browser for authentication
   - Token cached in `oauth_token.pickle` for future runs

3. **Verify ChromeDriver:**
   - System will auto-download ChromeDriver via `webdriver-manager`
   - Requires Chrome browser installed

### Running Individual Components

**Test Weather Fetcher:**
```bash
python weather_fetcher.py
```
Output: Console summary + `wind_farm_weather_TIMESTAMP.json`

**Test Impact Analyzer:**
```bash
python wind_impact_analyzer.py
```
Output: Console impact analysis for all farms

**Test Front Tracker:**
```bash
python weather_front_tracker.py
```
Output: `weather_fronts_map.html` with pressure systems and fronts

**Generate Complete Map:**
```bash
python weather_wind_impact_map.py
```
Output: 
- `weather_impact_map.html` (interactive)
- `weather_impact_map.png` (screenshot)
- Uploaded to Google Drive
- Inserted in Google Sheets

### Customization

**Toggle Map Layers:**
Edit `MAP_CONFIG` in `weather_wind_impact_map.py`:
```python
MAP_CONFIG = {
    'show_dnos': True,          # Show DNO boundaries
    'show_gsps': False,         # Show GSP boundaries
    'show_wind': True,          # Show wind farms
    'show_weather_impacts': True,  # Color-code by status
    'show_weather_fronts': True,   # Show weather symbols
    'center': [54.5, -2.5],     # Map center coordinates
    'zoom': 6.5                 # Initial zoom level
}
```

**Adjust Forecast Window:**
In `weather_fetcher.py`:
```python
forecast = self.get_hourly_forecast(lat, lon, hours=12)  # Change hours
```

**Modify Turbine Thresholds:**
In `wind_impact_analyzer.py`:
```python
CUT_IN_SPEED = 3.5   # Minimum generation speed
RATED_SPEED = 12.5   # Optimal speed
CUT_OUT_SPEED = 25.0 # Shutdown speed
```

**Change Screenshot Resolution:**
In `weather_wind_impact_map.py`:
```python
chrome_options.add_argument('--window-size=3840,3840')  # Base size
chrome_options.add_argument('--force-device-scale-factor=2')  # 2x scaling
```

---

## 📈 System Performance

### API Rate Limits
- **Open-Meteo:** 10,000 calls/day (free tier)
- **Current Usage:** ~40 calls per map generation
  - 15 farms × 2 calls (current + forecast) = 30
  - 25 grid points × 1 call = 25
  - Total: ~55 calls per run
- **Sustainable Frequency:** Up to 180 runs/day

### Processing Time
- Weather data fetch: ~30-45 seconds (15 farms)
- Grid weather fetch: ~25-35 seconds (25 points)
- Impact analysis: ~1 second
- Map generation: ~2 seconds
- Screenshot capture: ~5-8 seconds
- Google API upload: ~3-5 seconds
- **Total Runtime:** ~70-95 seconds per complete execution

### Data Freshness
- Weather data: Updated every 15 minutes (Open-Meteo)
- Recommended refresh: Every 30-60 minutes
- Historical BigQuery data: October 2025 (2 months old)

---

## 🔐 Authentication & Permissions

### Google Cloud Project
- **Project ID:** inner-cinema-476211-u9
- **Project Number:** 922809339325
- **Owner:** george.major@grid-smart.co.uk

### OAuth 2.0 Configuration
- **Application Type:** Desktop
- **Client ID:** 922809339325-6o85gncvdnqgoh4pvk1o9vhit1pb27ms.apps.googleusercontent.com
- **Scopes:**
  - `https://www.googleapis.com/auth/drive.file`
  - `https://www.googleapis.com/auth/spreadsheets`

### Google Sheets Access
- **Spreadsheet ID:** `12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI`
- **Sheet Name:** "Weather Impact Map"
- **URL:** https://docs.google.com/spreadsheets/d/12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI

### Required Permissions for New Users
To grant access to another user:

1. **Google Sheets:**
   - Share spreadsheet with user's email
   - Grant "Editor" access

2. **Google Cloud Console:**
   - Add user as "Viewer" or "Editor" to project
   - No additional IAM roles needed for OAuth flow

3. **OAuth Consent Screen:**
   - User must be added as "Test User" if app is in testing mode
   - Or publish app for general availability

---

## 🧪 Testing & Validation

### Unit Testing
Each module has a `main()` function for standalone testing:

```bash
# Test weather fetcher
python weather_fetcher.py

# Test impact analyzer
python wind_impact_analyzer.py

# Test front tracker
python weather_front_tracker.py
```

### Integration Testing
```bash
# Full system test
python weather_wind_impact_map.py
```

### Validation Checklist
- ✅ Weather data fetched successfully (15/15 farms)
- ✅ Forecast data available (12 hours)
- ✅ Impact analysis running (cut-in/cut-out detection)
- ✅ Map renders with all layers
- ✅ Weather fronts detected and displayed
- ✅ Screenshot captured at high resolution
- ✅ Upload to Drive successful
- ✅ Image inserted in Sheets
- ✅ Fleet summary statistics correct

---

## 🐛 Troubleshooting

### Common Issues

**1. OAuth Authentication Failed**
- Delete `oauth_token.pickle`
- Run script again to re-authenticate
- Ensure OAuth credentials file is present

**2. ChromeDriver Version Mismatch**
- System auto-updates via `webdriver-manager`
- Manual update: `brew upgrade --cask chromedriver` (macOS)

**3. API Rate Limit Exceeded**
- Open-Meteo: Wait 24 hours or use different IP
- Reduce grid_size in front tracker (5→3)

**4. Import Errors**
```bash
pip install -r requirements.txt
# Or manually:
pip install folium selenium webdriver-manager google-auth-oauthlib google-api-python-client
```

**5. BigQuery Authentication Issues**
```bash
gcloud auth application-default login
```

**6. Low Resolution Map**
- Check screenshot window size (should be 3840×3840)
- Verify device scale factor = 2
- Clear browser cache

---

## 📁 File Structure

```
Jibber Jabber Al knowing Dent/
├── weather_fetcher.py              # Weather data retrieval
├── wind_impact_analyzer.py         # Impact analysis engine
├── weather_front_tracker.py        # Front detection & symbols
├── weather_wind_impact_map.py      # Main orchestration script
├── auto_map_flexible_oauth.py      # Original map generator (legacy)
├── oauth_credentials.json          # OAuth client secrets
├── oauth_token.pickle              # Cached auth token
├── geojson_exports/
│   ├── offshore_wind_farms.geojson # Wind farm locations
│   ├── dno_boundaries.geojson      # DNO regions
│   └── gsp_boundaries.geojson      # GSP areas
├── weather_impact_map.html         # Interactive map output
├── weather_impact_map.png          # Screenshot output
├── wind_farm_weather_*.json        # Raw weather data exports
└── WEATHER_API_SETUP.md            # API configuration guide
```

---

## 🔮 Future Enhancements

### Planned Features
1. **Automated Scheduling** - Cron job for hourly updates
2. **Email Alerts** - Notify on critical events (shutdowns, icing)
3. **Historical Comparison** - Compare actual vs predicted generation
4. **Storm Path Animation** - Animated front movement over time
5. **API Endpoint** - REST API for external integrations
6. **Mobile Optimization** - Responsive design for mobile viewing
7. **Multi-Day Forecasts** - Extend to 7-day outlook
8. **Wind Rose Diagrams** - Directional wind frequency charts
9. **Capacity Planning** - Optimal dispatch recommendations
10. **Real-Time BigQuery Sync** - Live generation data instead of 2-month-old data

### Potential Integrations
- **National Grid ESO API** - Live balancing mechanism data
- **Elexon BMRS** - Settlement data and system prices
- **Met Office DataPoint** - UK-specific weather warnings
- **Copernicus Marine Service** - Enhanced marine forecasts
- **SCADA Integration** - Direct turbine telemetry (if available)

---

## 📞 Support & Contact

**Project Owner:** george.major@grid-smart.co.uk  
**Google Cloud Project:** inner-cinema-476211-u9  
**GitHub Repository:** [To be created]

---

## 📄 License

This system uses:
- **Open-Meteo API** - Attribution required, free for non-commercial use
- **Google Maps/Drive/Sheets APIs** - Subject to Google Cloud terms
- **BigQuery** - Google Cloud Platform billing applies

---

## 🙏 Acknowledgments

- **Open-Meteo** - Free weather API (https://open-meteo.com)
- **Folium** - Python mapping library
- **Selenium** - Browser automation
- **Google Cloud Platform** - API infrastructure
- **OpenStreetMap** - Base map tiles

---

**Last Updated:** 2025-12-30  
**System Version:** 1.0  
**Documentation Version:** 1.0

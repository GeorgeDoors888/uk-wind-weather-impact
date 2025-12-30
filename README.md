# UK Offshore Wind Farm Weather Impact System

Real-time weather monitoring and operational impact forecasting for UK offshore wind farms with power interconnector visualization.

## Features ✨

- **🌦️ Real-time Weather:** Live data from Open-Meteo API (free, no key required)
- **⚡ Wind Farm Monitoring:** 15 major offshore wind farms (11.57 GW total capacity)
- **🔌 Power Interconnectors:** 12 subsea cables to Europe (10.8 GW capacity)
- **🗺️ DNO & GSP Boundaries:** UK distribution network operator regions and grid supply points
- **📰 Meteorological Symbols:** Newspaper-style weather fronts, pressure systems, wind arrows
- **🎯 Impact Analysis:** Predicts shutdowns, icing risk, sub-optimal conditions
- **📊 Google Sheets Integration:** Automated dashboard updates via OAuth
- **📈 12-Hour Forecasting:** Hourly predictions with ETA for weather events
- **🎨 High-Resolution Maps:** 7680×7680 pixel professional visualizations

**Live Dashboard:** [View on Google Sheets](https://docs.google.com/spreadsheets/d/12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI)

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/GeorgeDoors888/uk-wind-weather-impact.git
cd uk-wind-weather-impact

# Install dependencies
pip install -r requirements.txt

# Run the main system
python weather_wind_impact_map.py

# Or generate all map variants
python generate_all_maps.py
```

## 📦 What's Included

### Core Components
- ✅ **weather_fetcher.py** - Real-time weather data from Open-Meteo
- ✅ **wind_impact_analyzer.py** - Operational impact analysis
- ✅ **weather_front_tracker.py** - Meteorological front detection
- ✅ **weather_wind_impact_map.py** - Main orchestration script
- ✅ **generate_all_maps.py** - Create multiple specialized map views

### Data Files
- ✅ **interconnectors.json** - 12 UK power interconnectors
- ✅ **geojson_exports/offshore_wind_farms.geojson** - 15 offshore wind farms
- ✅ **geojson_exports/dno_boundaries.geojson** - 14 DNO regions
- ✅ **geojson_exports/gsp_boundaries.geojson** - 100 GSP areas

### Documentation
- ✅ **WEATHER_IMPACT_SYSTEM_DOCUMENTATION.md** - Complete system guide
- ✅ **INTERCONNECTORS_GUIDE.md** - Power interconnector reference
- ✅ **COLLABORATION_GUIDE.md** - Team collaboration setup

## 🔌 Power Interconnectors

The system visualizes 12 UK power interconnectors:

| Connection | Capacity | Status |
|------------|----------|--------|
| France (IFA, IFA2, ElecLink) | 4,000 MW | Operational |
| Norway (North Sea Link) | 1,400 MW | Operational |
| Denmark (Viking Link) | 1,400 MW | Operational |
| Netherlands (BritNed) | 1,000 MW | Operational |
| Belgium (Nemo Link) | 1,000 MW | Operational |
| Germany (NeuConnect) | 1,400 MW | Under Construction |
| Ireland (EWIC, Greenlink) | 1,000 MW | 1 operational, 1 under construction |
| N. Ireland (Moyle) | 500 MW | Operational |
| Iceland (IceLink) | 1,000 MW | Proposed |

**Total Capacity:** 10.8 GW (7.9 GW operational)

See [INTERCONNECTORS_GUIDE.md](INTERCONNECTORS_GUIDE.md) for full details.

## Prerequisites 📋

1. **Python 3.8+**
2. **Google Cloud Project** with:
   - Drive API enabled
   - Sheets API enabled
   - BigQuery API enabled (optional, for historical data)
3. **OAuth 2.0 Credentials:**
   - Create Desktop Application credentials
   - Download as `oauth_credentials.json`

## Setup Instructions 🚀

### 1. Google Cloud Setup

#### Create OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. Application type: **Desktop app**
6. Download JSON and save as `oauth_credentials.json`

### 2. Local Setup

#### Clone/Download the Repository
```bash
cd "/Users/georgemajor/Jibber Jabber Al knowing Dent"
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or with virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

#### Configure Environment
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your actual values
nano .env
```

Update `.env` with:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/Users/georgemajor/path/to/service-account-key.json
DRIVE_FOLDER_ID=your_actual_drive_folder_id
SHEET_ID=your_actual_google_sheet_id
BQ_PROJECT_ID=jibber-jabber-knowledge
BQ_DATASET_ID=thesis_index
BQ_TABLE_ID=energy_theses
```

## Usage 🎯

### Run the Harvester
```bash
python energy_thesis_harvester.py
```

### What It Does
1. **Searches** each repository for energy-related theses
2. **Filters** by keywords (energy, solar, wind, battery, grid, etc.)
3. **Downloads** PDFs to `downloads_energy_theses/`
4. **Extracts** metadata (title, author, year)
5. **Uploads** to Google Drive
6. **Logs** to Google Sheet (one row per thesis)
7. **Indexes** in BigQuery for analysis
8. **Tracks** downloaded URLs to prevent duplicates

### Customize Harvesting Limits
Edit the `limit` parameter in `energy_thesis_harvester.py`:
```python
# Around line 700
recs = h(limit=10)  # Change to 50, 100, etc.
```

⚠️ **Be respectful**: Start with small limits (10-20) and increase gradually.

## Output Files 📁

```
downloads_energy_theses/     # Downloaded PDFs
downloaded_urls.log          # Duplicate prevention log
.env                         # Your credentials (keep private!)
```

## Repositories Covered 🌍

| University | Repository | Search Strategy |
|------------|------------|-----------------|
| Harvard | DASH | DSpace API, bitstream links |
| MIT | DSpace | Thesis filter, energy keywords |
| Cambridge | Apollo | Handle-based, OA filter |
| Oxford | ORA | Open access flag, energy query |
| UCL | Discovery | Advanced search, energy+thesis |
| Imperial | Spiral | DSpace, energy filter |
| Edinburgh | ERA | Thesis type, energy keywords |
| CORE | CORE.ac.uk | Global aggregator, PDF links |
| UK (All) | EThOS | British Library, OA theses |

## BigQuery Schema 📊

Table: `jibber-jabber-knowledge.thesis_index.energy_theses`

| Field | Type | Description |
|-------|------|-------------|
| title | STRING | Thesis title |
| author | STRING | Author name(s) |
| year | INTEGER | Publication year |
| university | STRING | Institution |
| source_repo | STRING | Repository name |
| pdf_url | STRING | Original PDF URL |
| local_filename | STRING | Downloaded filename |
| drive_file_id | STRING | Google Drive file ID |

### Example Query
```sql
-- Count by university
SELECT university, COUNT(*) as thesis_count
FROM `jibber-jabber-knowledge.thesis_index.energy_theses`
GROUP BY university
ORDER BY thesis_count DESC;

-- Find recent battery research
SELECT title, author, year, university
FROM `jibber-jabber-knowledge.thesis_index.energy_theses`
WHERE LOWER(title) LIKE '%battery%'
  AND year >= 2020
ORDER BY year DESC;
```

## Async/Parallel Version 🚀

For massive parallel downloading (10-100x faster), see `energy_thesis_harvester_async.py` (coming next).

## Legal & Ethical Considerations ⚖️

- ✅ **Only downloads open-access** content
- ✅ **Respects robots.txt** and institutional policies
- ✅ **Rate-limited** (1 second between requests)
- ✅ **User-Agent** identifies the bot
- ❌ **Does NOT** bypass paywalls or access restrictions
- ❌ **Does NOT** download copyrighted material

## Troubleshooting 🔧

### "Permission denied" on BigQuery
- Check service account has `BigQuery Data Editor` role
- Verify dataset exists: `bq ls jibber-jabber-knowledge:`

### "File not found" on Drive upload
- Confirm service account email is shared with the folder
- Check folder ID is correct in `.env`

### "Invalid credentials"
- Verify JSON path in `GOOGLE_APPLICATION_CREDENTIALS`
- Ensure JSON file is readable: `cat service-account-key.json`

### No PDFs found
- Some repositories block scrapers → check with `curl`
- HTML structure may have changed → update selectors
- Try different keywords or repositories

## Cost Estimate 💰

For 100,000 words (typical thesis ~50k words):

| Service | Usage | Cost |
|---------|-------|------|
| BigQuery Storage | <1 MB | **Free** (10 GB free tier) |
| BigQuery Queries | <1 GB | **Free** (1 TB free tier) |
| Google Drive | 15 GB free | **Free** (up to ~150 theses) |
| Google Sheets | <10k rows | **Free** |

**Total**: £0.00/month for typical usage

## Roadmap 🗺️

- [x] Multi-repository harvester
- [x] Energy keyword filtering
- [x] Drive upload
- [x] Sheets logging
- [x] BigQuery indexing
- [ ] Async/parallel version (10-100x faster)
- [ ] Topic classification (ML-based)
- [ ] Auto-summarization (LLM)
- [ ] Web dashboard (Streamlit/Dash)
- [ ] Email alerts for new theses
- [ ] Citation network analysis

## Support 💬

Issues? Questions?
- Check logs in terminal output
- Review `downloaded_urls.log` for duplicates
- Verify Google Cloud permissions

## License 📄

MIT License - Use responsibly and ethically.

---

**Built for Upowerenergy** | Research Automation Platform

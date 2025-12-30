# Energy Thesis Harvester 🎓⚡

Automated system to download, catalog, and index open-access PhD theses related to energy from major universities worldwide.

## Features ✨

- **9 Major Repositories**: Harvard, MIT, Cambridge, Oxford, UCL, Imperial, Edinburgh, CORE, British Library EThOS
- **Smart Filtering**: Only downloads energy-related theses using keyword matching
- **Metadata Extraction**: Captures title, author, year, university from institutional metadata
- **Google Drive Integration**: Uploads PDFs to specified Drive folder
- **Google Sheets Logging**: Maintains comprehensive spreadsheet log
- **BigQuery Indexing**: Creates searchable database for analytics and dashboards
- **Duplicate Prevention**: Maintains local log to avoid re-downloading

## Prerequisites 📋

1. **Python 3.8+**
2. **Google Cloud Project** with:
   - Drive API enabled
   - Sheets API enabled
   - BigQuery API enabled
3. **Service Account** with permissions:
   - Drive: Editor
   - Sheets: Editor
   - BigQuery: Data Editor

## Setup Instructions 🚀

### 1. Google Cloud Setup

#### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: `jibber-jabber-knowledge` (or your preferred name)
3. Note your Project ID

#### Enable Required APIs
```bash
# Enable APIs via Cloud Console or gcloud CLI:
gcloud services enable drive.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable bigquery.googleapis.com
```

#### Create Service Account
1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: `thesis-harvester`
4. Grant roles:
   - BigQuery Data Editor
   - (Drive/Sheets permissions are via sharing, not IAM)
5. Click **Done**
6. Click on the service account → **Keys** tab
7. **Add Key** → **Create New Key** → **JSON**
8. Save the JSON file securely (e.g., `service-account-key.json`)

#### Create Google Drive Folder
1. Create a folder in Google Drive (e.g., "Energy Theses")
2. Right-click → **Share**
3. Add your service account email (found in the JSON file: `client_email`)
4. Give it **Editor** permissions
5. Copy the folder ID from URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`

#### Create Google Sheet
1. Create a new Google Sheet (e.g., "Thesis Harvest Log")
2. Share with service account email (Editor permissions)
3. Copy Sheet ID from URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`

#### Create BigQuery Dataset
```bash
# Via gcloud CLI:
bq mk --dataset jibber-jabber-knowledge:thesis_index

# Or via Cloud Console:
# BigQuery → SQL Workspace → Create Dataset
# Dataset ID: thesis_index
# Location: US (or your preference)
```

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

# Collaboration Guide

## GitHub Repository

**🌐 Repository URL:** https://github.com/GeorgeDoors888/uk-wind-weather-impact

## Granting Access to Collaborators

### Option 1: Via GitHub Web Interface (Recommended)

1. Go to https://github.com/GeorgeDoors888/uk-wind-weather-impact
2. Click **Settings** (top right)
3. Click **Collaborators** (left sidebar)
4. Click **Add people**
5. Enter GitHub username or email
6. Select permission level:
   - **Read**: View code only
   - **Triage**: Read + manage issues
   - **Write**: Read + push changes ⭐ Recommended
   - **Maintain**: Write + manage settings
   - **Admin**: Full access

### Option 2: Via GitHub CLI

```bash
# Grant write access
gh api repos/GeorgeDoors888/uk-wind-weather-impact/collaborators/USERNAME -X PUT

# Grant admin access
gh api repos/GeorgeDoors888/uk-wind-weather-impact/collaborators/USERNAME -X PUT -f permission=admin
```

## For Collaborators: Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/GeorgeDoors888/uk-wind-weather-impact.git
cd uk-wind-weather-impact
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Authentication

You'll need:
- **Google OAuth credentials** (`oauth_credentials.json`)
- **GeoJSON data files** (in `geojson_exports/`)

Contact george.major@grid-smart.co.uk to receive:
1. OAuth credentials file
2. GeoJSON boundary and wind farm data
3. Access to Google Sheets dashboard

Place `oauth_credentials.json` in project root (it's git-ignored for security).

### 4. Run the System

```bash
python weather_wind_impact_map.py
```

First run will open browser for Google OAuth authorization.

## VS Code Integration

### Set Up Remote Repository

1. Open VS Code
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows)
3. Type "Git: Clone"
4. Paste: `https://github.com/GeorgeDoors888/uk-wind-weather-impact.git`
5. Choose local folder

### Sign In to GitHub

1. Click **Accounts** icon (bottom left)
2. Click **Sign in with GitHub**
3. Authorize VS Code in browser

### Sync Changes

- **Pull latest**: Click ↓ icon (bottom left) or `Cmd+Shift+P` → "Git: Pull"
- **Push changes**: Click ↑ icon (bottom left) or `Cmd+Shift+P` → "Git: Push"

### Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "GitHub.copilot",
    "eamodio.gitlens",
    "ms-toolsai.jupyter"
  ]
}
```

## Working with Multiple Sessions

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, then commit
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature/your-feature-name

# Create pull request on GitHub
# After review, merge to main
```

### Avoiding Conflicts

1. **Always pull before starting work:**
   ```bash
   git pull origin main
   ```

2. **Communicate with team** about who's working on what

3. **Use separate branches** for independent features

4. **Test before pushing:**
   ```bash
   python weather_wind_impact_map.py
   ```

## File Structure

```
uk-wind-weather-impact/
├── weather_fetcher.py              # Weather data retrieval
├── wind_impact_analyzer.py         # Impact analysis
├── weather_front_tracker.py        # Front detection
├── weather_wind_impact_map.py      # Main orchestration
├── WEATHER_IMPACT_SYSTEM_DOCUMENTATION.md
├── README.md
├── requirements.txt
├── .gitignore
├── geojson_exports/                # Not in repo (too large)
│   ├── offshore_wind_farms.geojson
│   ├── dno_boundaries.geojson
│   └── gsp_boundaries.geojson
└── oauth_credentials.json          # Not in repo (secret)
```

## Security Notes

⚠️ **Never commit these files:**
- `oauth_credentials.json` (OAuth secrets)
- `oauth_token.pickle` (Cached tokens)
- `*.key`, `*.pem` (Private keys)
- `.env` (Environment variables)

These are already in `.gitignore`.

## Support

**Issues:** https://github.com/GeorgeDoors888/uk-wind-weather-impact/issues  
**Email:** george.major@grid-smart.co.uk  
**Google Sheets Dashboard:** [View Live](https://docs.google.com/spreadsheets/d/12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI)

## Quick Commands Reference

```bash
# Clone repository
git clone https://github.com/GeorgeDoors888/uk-wind-weather-impact.git

# Update from remote
git pull

# Create branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "Your message"

# Push changes
git push origin main

# View status
git status

# View history
git log --oneline

# Discard local changes
git checkout -- filename.py
```

---

**Repository Created:** 2025-12-30  
**Owner:** George Major (GeorgeDoors888)  
**License:** MIT

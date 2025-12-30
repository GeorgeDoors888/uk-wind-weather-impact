#!/usr/bin/env python3
"""
Weather-Aware Wind Farm Map Generator
Integrates real-time weather data, impact analysis, and interactive mapping
"""

import json
import folium
from datetime import datetime
from weather_fetcher import WeatherFetcher
from wind_impact_analyzer import WindImpactAnalyzer
from weather_front_tracker import WeatherFrontTracker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuration
MAP_CONFIG = {
    'show_dnos': True,
    'show_gsps': False,
    'show_wind': True,
    'show_weather_impacts': True,  # Color-code by weather status
    'show_weather_fronts': True,   # Show pressure systems and fronts
    'center': [54.5, -2.5],
    'zoom': 6.5
}

# File paths
DNO_GEOJSON = 'geojson_exports/dno_boundaries.geojson'
GSP_GEOJSON = 'geojson_exports/gsp_boundaries.geojson'
WIND_GEOJSON = 'geojson_exports/offshore_wind_farms.geojson'

# OAuth settings
SCOPES = ['https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '12LaxizI4ASJduSMRYasrQEBvIku3YDiE3wbjanaIFyI'

# Color schemes
DNO_COLORS = {
    'ENWL': '#e74c3c', 'NGED': '#3498db', 'SSEN': '#2ecc71',
    'SPEN': '#f39c12', 'UKPN': '#9b59b6', 'NPG': '#1abc9c', 'WPD': '#e67e22'
}

# Weather impact colors
IMPACT_COLORS = {
    'green': '#27ae60',    # Normal operation
    'yellow': '#f39c12',   # Sub-optimal
    'orange': '#e67e22',   # Icing risk
    'red': '#e74c3c'       # Shutdown
}


def get_oauth_credentials():
    """Get OAuth credentials for Google APIs"""
    creds = None
    
    if os.path.exists('oauth_token.pickle'):
        with open('oauth_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('oauth_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def generate_weather_impact_map():
    """Generate map with weather-aware wind farm markers"""
    
    print("=" * 80)
    print("🌦️  WEATHER-AWARE WIND FARM MAP GENERATOR")
    print("=" * 80)
    print()
    
    # Initialize components
    print("🔧 Initializing weather fetcher and impact analyzer...")
    fetcher = WeatherFetcher()
    analyzer = WindImpactAnalyzer()
    front_tracker = WeatherFrontTracker() if MAP_CONFIG['show_weather_fronts'] else None
    
    # Fetch weather data for all wind farms
    print("\n📡 Fetching live weather data...")
    weather_data = fetcher.fetch_all_wind_farms(WIND_GEOJSON, include_forecast=True, include_marine=False)
    
    # Analyze impacts
    print("\n⚡ Analyzing operational impacts...")
    impact_results = {}
    for farm in weather_data:
        if 'current' in farm and 'forecast' in farm:
            current_status = analyzer.analyze_current_conditions(farm['current'])
            events = analyzer.analyze_forecast(farm['forecast'])
            overall = analyzer.get_overall_status(current_status, events)
            impact_results[farm['name']] = overall
    
    # Create map
    print("\n🗺️  Creating map...")
    m = folium.Map(
        location=MAP_CONFIG['center'],
        zoom_start=MAP_CONFIG['zoom'],
        tiles='OpenStreetMap'
    )
    
    # Add DNO boundaries if enabled
    if MAP_CONFIG['show_dnos']:
        print("🎨 Adding DNO boundaries...")
        with open(DNO_GEOJSON, 'r') as f:
            dno_data = json.load(f)
        
        for feature in dno_data['features']:
            dno_code = feature['properties']['dno_code']
            dno_name = feature['properties']['dno_full_name']
            color = DNO_COLORS.get(dno_code, '#95a5a6')
            
            folium.GeoJson(
                feature,
                style_function=lambda x, c=color: {
                    'fillColor': c,
                    'color': c,
                    'weight': 3,
                    'fillOpacity': 0.2
                },
                tooltip=f"{dno_name} ({dno_code})"
            ).add_to(m)
    
    # Add GSP boundaries if enabled
    if MAP_CONFIG['show_gsps']:
        print("🎨 Adding GSP boundaries...")
        with open(GSP_GEOJSON, 'r') as f:
            gsp_data = json.load(f)
        
        for feature in gsp_data['features']:
            gsp_id = feature['properties']['gsp_id']
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'fillColor': '#34495e',
                    'color': '#34495e',
                    'weight': 1,
                    'fillOpacity': 0.05,
                    'dashArray': '5, 5'
                },
                tooltip=f"GSP: {gsp_id}"
            ).add_to(m)
    
    # Add wind farms with weather-aware colors
    if MAP_CONFIG['show_wind']:
        print("🎨 Adding weather-aware wind farm markers...")
        
        for farm in weather_data:
            if 'current' not in farm:
                continue
            
            coords = [farm['location']['lat'], farm['location']['lon']]
            name = farm['name']
            capacity_mw = farm['capacity_mw']
            capacity_gw = capacity_mw / 1000
            
            # Get impact analysis
            impact = impact_results.get(name, {})
            current = farm['current']
            
            # Determine color based on weather impact
            if MAP_CONFIG['show_weather_impacts'] and impact:
                color = IMPACT_COLORS[impact['priority_color']]
                fill_color = color
            else:
                color = '#16a085'
                fill_color = '#1abc9c'
            
            # Build detailed popup HTML
            popup_html = f"""
            <div style="font-family: Arial; min-width: 300px;">
                <h3 style="margin: 0 0 10px 0; color: {color};">{name}</h3>
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>Capacity:</b></td><td>{capacity_gw:.2f} GW ({capacity_mw:.0f} MW)</td></tr>
                    <tr><td colspan="2" style="padding-top: 10px;"><b>⚡ Current Status</b></td></tr>
            """
            
            if impact:
                current_status = impact['current']
                popup_html += f"""
                    <tr><td><b>Status:</b></td><td style="color: {color};">{current_status['status'].upper()}</td></tr>
                    <tr><td><b>Capacity Factor:</b></td><td>{current_status['capacity_factor']*100:.0f}%</td></tr>
                    <tr><td><b>Power Output:</b></td><td>{capacity_mw * current_status['capacity_factor']:.0f} MW</td></tr>
                """
            
            popup_html += f"""
                <tr><td colspan="2" style="padding-top: 10px;"><b>🌬️ Current Weather</b></td></tr>
                <tr><td><b>Wind Speed:</b></td><td>{current['wind_speed_ms']:.1f} m/s ({current['wind_speed_ms']*3.6:.1f} km/h)</td></tr>
                <tr><td><b>Wind Direction:</b></td><td>{current['wind_direction_deg']}°</td></tr>
                <tr><td><b>Gusts:</b></td><td>{current['wind_gust_ms']:.1f} m/s</td></tr>
                <tr><td><b>Temperature:</b></td><td>{current['temperature_c']:.1f}°C (feels {current['feels_like_c']:.1f}°C)</td></tr>
                <tr><td><b>Humidity:</b></td><td>{current['humidity_pct']}%</td></tr>
                <tr><td><b>Conditions:</b></td><td>{current['description']}</td></tr>
            """
            
            # Add marine data if available
            if 'marine_forecast' in farm and farm['marine_forecast']:
                marine = farm['marine_forecast'][0]
                popup_html += f"""
                    <tr><td colspan="2" style="padding-top: 10px;"><b>🌊 Sea Conditions</b></td></tr>
                    <tr><td><b>Wave Height:</b></td><td>{marine['wave_height_m']:.1f}m</td></tr>
                    <tr><td><b>Wave Period:</b></td><td>{marine['wave_period_s']:.0f}s</td></tr>
                """
            
            # Add upcoming events
            if impact and impact['upcoming_events']:
                popup_html += f"""
                    <tr><td colspan="2" style="padding-top: 10px;"><b>⚠️ Upcoming Events</b></td></tr>
                """
                for event in impact['upcoming_events'][:3]:
                    eta_text = f"{event['eta_hours']:.1f}h" if event['eta_hours'] > 0 else "NOW"
                    duration_text = f", {event['duration_hours']:.1f}h duration" if event['duration_hours'] else ""
                    popup_html += f"""
                        <tr><td colspan="2" style="color: #e74c3c;"><small>• {event['type'].upper()}: ETA {eta_text}{duration_text}</small></td></tr>
                    """
            
            popup_html += """
                </table>
            </div>
            """
            
            # Create tooltip
            tooltip_text = f"{name}: {capacity_gw:.2f} GW"
            if impact:
                tooltip_text += f" | {impact['current']['status'].upper()} ({impact['current']['capacity_factor']*100:.0f}%)"
            
            # Add marker sized by capacity (larger for visibility)
            radius = 15 + (capacity_gw * 5)
            folium.CircleMarker(
                location=coords,
                radius=radius,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=tooltip_text,
                color=color,
                fill=True,
                fillColor=fill_color,
                fillOpacity=0.8,
                weight=4
            ).add_to(m)
    
    # Add weather fronts and pressure systems
    if MAP_CONFIG['show_weather_fronts'] and front_tracker:
        print("🌀 Adding weather fronts and pressure systems...")
        
        # Define UK bounds
        uk_bounds = {
            'north': 59.0,
            'south': 49.5,
            'west': -8.0,
            'east': 2.0
        }
        
        # Get grid weather data
        grid_data = front_tracker.get_grid_weather(uk_bounds, grid_size=5)
        
        # Detect systems and fronts
        systems = front_tracker.detect_pressure_systems(grid_data)
        fronts = front_tracker.detect_fronts(grid_data)
        
        # Add to map
        front_tracker.add_fronts_to_map(m, grid_data, systems, fronts)
    
    # Add legend
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; right: 50px; width: 350px; 
                background-color: white; border: 3px solid grey; z-index: 9999; 
                padding: 20px; font-size: 16px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin: 0 0 15px 0; font-size: 20px;">UK Energy Map - Weather Impact</h3>
        <p style="margin: 8px 0; font-weight: bold;">Wind Farm Status:</p>
        <p style="margin: 5px 0; font-size: 15px;">🟢 <span style="color: {IMPACT_COLORS['green']}; font-size: 18px;">●</span> Normal Operation (>80% capacity)</p>
        <p style="margin: 5px 0; font-size: 15px;">🟡 <span style="color: {IMPACT_COLORS['yellow']}; font-size: 18px;">●</span> Sub-optimal Wind (<80% capacity)</p>
        <p style="margin: 5px 0; font-size: 15px;">🟠 <span style="color: {IMPACT_COLORS['orange']}; font-size: 18px;">●</span> Icing Risk (temp <0°C)</p>
        <p style="margin: 5px 0; font-size: 15px;">🔴 <span style="color: {IMPACT_COLORS['red']}; font-size: 18px;">●</span> Shutdown (wind >25 m/s)</p>
    """
    
    if MAP_CONFIG['show_weather_fronts']:
        legend_html += """
        <p style="margin: 15px 0 8px 0; font-weight: bold;">Weather Symbols:</p>
        <p style="margin: 5px 0; font-size: 15px;"><span style="color: #FF0000; font-weight: bold; font-size: 20px;">H</span> High Pressure | <span style="color: #0000FF; font-weight: bold; font-size: 20px;">L</span> Low Pressure</p>
        <p style="margin: 5px 0; font-size: 15px;"><span style="color: #0000FF; font-size: 18px;">▼</span> Cold Front | <span style="color: #FF0000; font-size: 18px;">▲</span> Warm Front</p>
        <p style="margin: 5px 0; font-size: 18px;">☀☁🌧❄⛈ Weather | ↑→↓← Wind</p>
        """
    
    legend_html += f"""
        <p style="margin: 15px 0 0 0; font-size: 13px;"><i>Data: Open-Meteo • Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</i></p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    output_file = 'weather_impact_map.html'
    m.save(output_file)
    print(f"💾 Saved interactive map: {os.path.abspath(output_file)}")
    
    return output_file, impact_results


def capture_screenshot(html_file: str, output_png: str = 'weather_impact_map.png'):
    """Capture high-resolution screenshot of the map"""
    print("\n📸 Capturing screenshot...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=3840,3840')
    chrome_options.add_argument('--force-device-scale-factor=2')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    file_url = f'file://{os.path.abspath(html_file)}'
    driver.get(file_url)
    time.sleep(5)
    
    driver.save_screenshot(output_png)
    driver.quit()
    
    print(f"✅ Screenshot saved: {output_png}")
    return output_png


def upload_to_drive_oauth(file_path: str, creds):
    """Upload file to Google Drive"""
    print("\n📤 Uploading to Drive...")
    
    drive_service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': os.path.basename(file_path),
        'mimeType': 'image/png'
    }
    
    media = MediaFileUpload(file_path, mimetype='image/png', resumable=True)
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()
    
    file_id = file.get('id')
    
    # Make file publicly viewable
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    print(f"✅ Uploaded! File ID: {file_id}")
    
    return image_url


def insert_image_in_sheet(image_url: str, creds, sheet_name: str = 'Weather Impact Map'):
    """Insert image in Google Sheet"""
    print("\n📊 Inserting into Sheet...")
    
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # Create or clear the sheet
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': [{'addSheet': {'properties': {'title': sheet_name}}}]}
        ).execute()
    except:
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A1:Z1000'
        ).execute()
    
    # Insert image formula
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{sheet_name}!A1',
        valueInputOption='USER_ENTERED',
        body={'values': [[f'=IMAGE("{image_url}")']]}
    ).execute()
    
    print(f"✅ Image inserted in '{sheet_name}' tab!")


def main():
    """Main execution"""
    # Generate map
    html_file, impact_results = generate_weather_impact_map()
    
    # Capture screenshot
    png_file = capture_screenshot(html_file)
    
    # Get OAuth credentials
    print("\n🔐 Authenticating with Google...")
    creds = get_oauth_credentials()
    
    # Upload to Drive
    image_url = upload_to_drive_oauth(png_file, creds)
    
    # Insert in Sheet
    insert_image_in_sheet(image_url, creds)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 WEATHER IMPACT SUMMARY")
    print("=" * 80)
    
    status_counts = {'green': 0, 'yellow': 0, 'orange': 0, 'red': 0}
    total_capacity = 0
    total_output = 0
    
    # Load wind farms for capacity calculation
    with open(WIND_GEOJSON, 'r') as f:
        wind_farms_geojson = json.load(f)
    
    for name, impact in impact_results.items():
        status_counts[impact['priority_color']] += 1
        # Find capacity from wind farms data
        for feature in wind_farms_geojson['features']:
            if feature['properties']['name'] == name:
                capacity_mw = feature['properties']['capacity_mw']
                total_capacity += capacity_mw
                total_output += capacity_mw * impact['current']['capacity_factor']
                break
    
    print(f"\n🏭 Fleet Status:")
    print(f"   🟢 Normal: {status_counts['green']} farms")
    print(f"   🟡 Sub-optimal: {status_counts['yellow']} farms")
    print(f"   🟠 Icing Risk: {status_counts['orange']} farms")
    print(f"   🔴 Shutdown: {status_counts['red']} farms")
    print(f"\n⚡ Power Output:")
    print(f"   Total Capacity: {total_capacity/1000:.2f} GW")
    print(f"   Current Output: {total_output/1000:.2f} GW ({total_output/total_capacity*100:.0f}%)")
    
    print("\n✅ Complete!")
    print(f"🌐 Open: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == '__main__':
    main()

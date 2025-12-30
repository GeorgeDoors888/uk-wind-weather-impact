#!/usr/bin/env python3
"""
Weather Data Fetcher for Offshore Wind Farms
Fetches real-time and forecast weather data from Open-Meteo API (free, no key required)
Also integrates with BigQuery for historical wind generation data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.cloud import bigquery

class WeatherFetcher:
    """Fetch weather data for offshore wind farm locations using Open-Meteo API"""
    
    def __init__(self, bigquery_project: str = "inner-cinema-476211-u9"):
        """
        Initialize weather fetcher
        
        Args:
            bigquery_project: GCP project ID for BigQuery access
        """
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.marine_url = "https://marine-api.open-meteo.com/v1/marine"
        self.bq_client = bigquery.Client(project=bigquery_project) if bigquery_project else None
        
    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """
        Get current weather conditions at a location using Open-Meteo
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dict with weather data including wind speed, direction, temp, humidity
        """
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'wind_speed_unit': 'ms',  # meters per second
            'timezone': 'UTC'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            current = data['current']
            
            return {
                'timestamp': datetime.fromisoformat(current['time'].replace('Z', '+00:00')),
                'wind_speed_ms': current['wind_speed_10m'],
                'wind_direction_deg': current['wind_direction_10m'],
                'wind_gust_ms': current['wind_gusts_10m'],
                'temperature_c': current['temperature_2m'],
                'feels_like_c': current['apparent_temperature'],
                'humidity_pct': current['relative_humidity_2m'],
                'pressure_hpa': current['pressure_msl'],
                'clouds_pct': current['cloud_cover'],
                'precipitation_mm': current['precipitation'],
                'weather_code': current['weather_code'],
                'description': self._weather_code_description(current['weather_code'])
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching current weather for ({lat}, {lon}): {e}")
            return None
    
    def get_hourly_forecast(self, lat: float, lon: float, hours: int = 12) -> List[Dict]:
        """
        Get hourly weather forecast using Open-Meteo
        
        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast (Open-Meteo supports up to 168 hours / 7 days)
            
        Returns:
            List of forecast dicts, one per hour
        """
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,pressure_msl,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'wind_speed_unit': 'ms',
            'timezone': 'UTC',
            'forecast_hours': hours
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            hourly = data['hourly']
            
            forecasts = []
            for i in range(min(hours, len(hourly['time']))):
                forecasts.append({
                    'timestamp': datetime.fromisoformat(hourly['time'][i].replace('Z', '+00:00')),
                    'wind_speed_ms': hourly['wind_speed_10m'][i],
                    'wind_direction_deg': hourly['wind_direction_10m'][i],
                    'wind_gust_ms': hourly['wind_gusts_10m'][i],
                    'temperature_c': hourly['temperature_2m'][i],
                    'humidity_pct': hourly['relative_humidity_2m'][i],
                    'pressure_hpa': hourly['pressure_msl'][i],
                    'clouds_pct': hourly['cloud_cover'][i],
                    'precipitation_mm': hourly['precipitation'][i],
                    'weather_code': hourly['weather_code'][i],
                    'description': self._weather_code_description(hourly['weather_code'][i])
                })
            
            return forecasts
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching forecast for ({lat}, {lon}): {e}")
            return []
    
    def get_marine_forecast(self, lat: float, lon: float, hours: int = 12) -> List[Dict]:
        """
        Get marine-specific forecast (wave height, swell, etc.) using Open-Meteo Marine API
        
        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast
            
        Returns:
            List of marine forecast dicts
        """
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'wave_height,wave_direction,wave_period,wind_wave_height,swell_wave_height',
            'timezone': 'UTC',
            'forecast_hours': hours
        }
        
        try:
            response = requests.get(self.marine_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            hourly = data['hourly']
            
            forecasts = []
            for i in range(min(hours, len(hourly['time']))):
                forecasts.append({
                    'timestamp': datetime.fromisoformat(hourly['time'][i].replace('Z', '+00:00')),
                    'wave_height_m': hourly['wave_height'][i],
                    'wave_direction_deg': hourly['wave_direction'][i],
                    'wave_period_s': hourly['wave_period'][i],
                    'wind_wave_height_m': hourly['wind_wave_height'][i],
                    'swell_wave_height_m': hourly['swell_wave_height'][i]
                })
            
            return forecasts
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Marine forecast unavailable for ({lat}, {lon}): {e}")
            return []
    
    def _weather_code_description(self, code: int) -> str:
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, f"Code {code}")
    
    def get_wind_farm_weather(self, wind_farm: Dict, include_forecast: bool = True, include_marine: bool = True) -> Dict:
        """
        Get complete weather data for a wind farm
        
        Args:
            wind_farm: Wind farm dict with 'geometry' (Point coordinates) and 'properties'
            include_forecast: Whether to include forecast data
            include_marine: Whether to include marine forecast (waves, etc.)
            
        Returns:
            Dict with current conditions and optional forecast
        """
        coords = wind_farm['geometry']['coordinates']
        lon, lat = coords[0], coords[1]
        name = wind_farm['properties']['name']
        
        print(f"🌤️  Fetching weather for {name} ({lat:.2f}, {lon:.2f})...")
        
        result = {
            'name': name,
            'location': {'lat': lat, 'lon': lon},
            'capacity_mw': wind_farm['properties']['capacity_mw']
        }
        
        # Get current conditions
        current = self.get_current_weather(lat, lon)
        if current:
            result['current'] = current
        
        # Get forecast if requested
        if include_forecast:
            forecast = self.get_hourly_forecast(lat, lon, hours=12)
            if forecast:
                result['forecast'] = forecast
        
        # Get marine forecast if requested
        if include_marine:
            marine = self.get_marine_forecast(lat, lon, hours=12)
            if marine:
                result['marine_forecast'] = marine
        
        return result
    
    def get_bigquery_wind_generation(self, hours_back: int = 24) -> List[Dict]:
        """
        Get recent wind generation data from BigQuery
        
        Args:
            hours_back: Number of hours of historical data to fetch
            
        Returns:
            List of generation records
        """
        if not self.bq_client:
            return []
        
        query = f"""
        SELECT 
            startTime,
            fuelType,
            generation
        FROM `inner-cinema-476211-u9.uk_energy_prod.bmrs_fuelinst_dedup`
        WHERE fuelType = 'WIND'
        AND startTime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours_back} HOUR)
        ORDER BY startTime DESC
        LIMIT 1000
        """
        
        try:
            print(f"📊 Fetching wind generation data from BigQuery...")
            query_job = self.bq_client.query(query)
            results = []
            for row in query_job:
                results.append({
                    'timestamp': row.startTime,
                    'fuel_type': row.fuelType,
                    'generation_mw': row.generation
                })
            print(f"✅ Retrieved {len(results)} generation records")
            return results
        except Exception as e:
            print(f"❌ Error fetching BigQuery data: {e}")
            return []
    
    def fetch_all_wind_farms(self, geojson_path: str, include_forecast: bool = True, include_marine: bool = True) -> List[Dict]:
        """
        Fetch weather for all wind farms in a GeoJSON file
        
        Args:
            geojson_path: Path to wind farms GeoJSON file
            include_forecast: Whether to include forecast data
            include_marine: Whether to include marine forecast
            
        Returns:
            List of weather data dicts, one per wind farm
        """
        print(f"📂 Loading wind farms from {geojson_path}...")
        
        with open(geojson_path, 'r') as f:
            geojson = json.load(f)
        
        wind_farms = geojson['features']
        print(f"✅ Found {len(wind_farms)} wind farms\n")
        
        all_weather = []
        for farm in wind_farms:
            weather_data = self.get_wind_farm_weather(farm, include_forecast, include_marine)
            all_weather.append(weather_data)
        
        return all_weather
    
    def save_weather_data(self, weather_data: List[Dict], output_path: str):
        """Save weather data to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(weather_data, f, indent=2, default=str)
        print(f"\n💾 Saved weather data to {output_path}")


def main():
    """Test the weather fetcher"""
    print("=" * 80)
    print("🌊 OFFSHORE WIND FARM WEATHER FETCHER (Open-Meteo + BigQuery)")
    print("=" * 80)
    print()
    
    # Initialize fetcher (no API key needed for Open-Meteo!)
    fetcher = WeatherFetcher()
    
    # Fetch weather for all wind farms
    weather_data = fetcher.fetch_all_wind_farms(
        'geojson_exports/offshore_wind_farms.geojson',
        include_forecast=True,
        include_marine=True
    )
    
    # Optionally fetch BigQuery wind generation data
    # generation_data = fetcher.get_bigquery_wind_generation(hours_back=24)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"wind_farm_weather_{timestamp}.json"
    fetcher.save_weather_data(weather_data, output_file)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 WEATHER SUMMARY")
    print("=" * 80)
    
    for farm_weather in weather_data:
        if 'current' in farm_weather:
            current = farm_weather['current']
            print(f"\n🏭 {farm_weather['name']} ({farm_weather['capacity_mw']} MW)")
            print(f"   🌬️  Wind: {current['wind_speed_ms']:.1f} m/s ({current['wind_speed_ms'] * 3.6:.1f} km/h) from {current['wind_direction_deg']}°")
            print(f"   💨 Gusts: {current['wind_gust_ms']:.1f} m/s")
            print(f"   🌡️  Temp: {current['temperature_c']:.1f}°C (feels {current['feels_like_c']:.1f}°C)")
            print(f"   💧 Humidity: {current['humidity_pct']}%")
            print(f"   ☁️  Conditions: {current['description']}")
            
            # Show marine data if available
            if 'marine_forecast' in farm_weather and farm_weather['marine_forecast']:
                marine = farm_weather['marine_forecast'][0]
                print(f"   🌊 Waves: {marine['wave_height_m']:.1f}m @ {marine['wave_period_s']:.0f}s period")
    
    print("\n✅ Complete!")


if __name__ == '__main__':
    main()

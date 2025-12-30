#!/usr/bin/env python3
"""
Weather Front Tracker
Detects and visualizes weather fronts, pressure systems, and wind patterns
Uses standard meteorological symbols like newspaper weather maps
"""

import requests
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import folium
from folium import plugins

class WeatherFrontTracker:
    """Track weather fronts and pressure systems across UK"""
    
    # Standard meteorological symbols (Unicode)
    SYMBOLS = {
        'sun': '☀',
        'cloud': '☁',
        'rain': '🌧',
        'snow': '❄',
        'storm': '⛈',
        'wind': '💨',
        'fog': '🌫',
        'high_pressure': 'H',
        'low_pressure': 'L',
        'arrow_n': '↑',
        'arrow_ne': '↗',
        'arrow_e': '→',
        'arrow_se': '↘',
        'arrow_s': '↓',
        'arrow_sw': '↙',
        'arrow_w': '←',
        'arrow_nw': '↖'
    }
    
    def __init__(self):
        """Initialize weather front tracker"""
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    def get_grid_weather(self, bounds: Dict, grid_size: int = 5) -> List[Dict]:
        """
        Get weather data on a grid across the UK
        
        Args:
            bounds: {'north': lat, 'south': lat, 'west': lon, 'east': lon}
            grid_size: Number of points per side
            
        Returns:
            List of weather data points with location and conditions
        """
        print(f"📍 Fetching weather grid ({grid_size}x{grid_size} points)...")
        
        lats = np.linspace(bounds['south'], bounds['north'], grid_size)
        lons = np.linspace(bounds['west'], bounds['east'], grid_size)
        
        grid_data = []
        for lat in lats:
            for lon in lons:
                try:
                    params = {
                        'latitude': lat,
                        'longitude': lon,
                        'current': 'temperature_2m,pressure_msl,wind_speed_10m,wind_direction_10m,weather_code',
                        'hourly': 'temperature_2m,pressure_msl,wind_speed_10m,wind_direction_10m',
                        'forecast_hours': 6,
                        'wind_speed_unit': 'ms',
                        'timezone': 'UTC'
                    }
                    
                    response = requests.get(self.base_url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    current = data['current']
                    hourly = data['hourly']
                    
                    # Calculate pressure trend (rising/falling)
                    pressure_now = current['pressure_msl']
                    pressure_future = hourly['pressure_msl'][3] if len(hourly['pressure_msl']) > 3 else pressure_now
                    pressure_trend = pressure_future - pressure_now
                    
                    grid_data.append({
                        'lat': lat,
                        'lon': lon,
                        'temperature': current['temperature_2m'],
                        'pressure': pressure_now,
                        'pressure_trend': pressure_trend,
                        'wind_speed': current['wind_speed_10m'],
                        'wind_direction': current['wind_direction_10m'],
                        'weather_code': current['weather_code'],
                        'hourly_forecast': hourly
                    })
                except Exception as e:
                    print(f"⚠️  Error fetching grid point ({lat:.1f}, {lon:.1f}): {e}")
                    continue
        
        print(f"✅ Retrieved {len(grid_data)} grid points")
        return grid_data
    
    def detect_pressure_systems(self, grid_data: List[Dict]) -> List[Dict]:
        """
        Detect high and low pressure systems
        
        Args:
            grid_data: List of weather grid points
            
        Returns:
            List of pressure systems with location and type
        """
        print("🔍 Detecting pressure systems...")
        
        if len(grid_data) < 9:
            return []
        
        systems = []
        
        # Find local maxima and minima in pressure field
        for point in grid_data:
            # Get nearby points
            nearby = [p for p in grid_data 
                     if abs(p['lat'] - point['lat']) < 2 
                     and abs(p['lon'] - point['lon']) < 2
                     and p != point]
            
            if not nearby:
                continue
            
            # Check if this is a local maximum (high pressure)
            if all(point['pressure'] > n['pressure'] for n in nearby):
                if point['pressure'] > 1015:  # Typical high pressure threshold
                    systems.append({
                        'type': 'high',
                        'lat': point['lat'],
                        'lon': point['lon'],
                        'pressure': point['pressure'],
                        'symbol': self.SYMBOLS['high_pressure']
                    })
            
            # Check if this is a local minimum (low pressure)
            elif all(point['pressure'] < n['pressure'] for n in nearby):
                if point['pressure'] < 1010:  # Typical low pressure threshold
                    systems.append({
                        'type': 'low',
                        'lat': point['lat'],
                        'lon': point['lon'],
                        'pressure': point['pressure'],
                        'symbol': self.SYMBOLS['low_pressure']
                    })
        
        print(f"✅ Found {len(systems)} pressure systems")
        return systems
    
    def detect_fronts(self, grid_data: List[Dict]) -> List[Dict]:
        """
        Detect weather fronts (cold, warm, occluded)
        
        Args:
            grid_data: List of weather grid points
            
        Returns:
            List of detected fronts with location and type
        """
        print("🌀 Detecting weather fronts...")
        
        fronts = []
        
        # Sort by latitude for easier scanning
        sorted_data = sorted(grid_data, key=lambda x: x['lat'])
        
        # Look for sharp temperature gradients (indicating fronts)
        for i in range(len(sorted_data) - 1):
            p1 = sorted_data[i]
            p2 = sorted_data[i + 1]
            
            # Calculate temperature gradient
            temp_diff = abs(p2['temperature'] - p1['temperature'])
            distance = ((p2['lat'] - p1['lat'])**2 + (p2['lon'] - p1['lon'])**2)**0.5
            
            if distance > 0:
                gradient = temp_diff / distance
                
                # Strong gradient indicates a front
                if gradient > 1.5:  # degrees per degree of lat/lon
                    # Determine front type based on temperature change and pressure
                    if p2['temperature'] < p1['temperature']:
                        front_type = 'cold'
                        color = '#0000FF'  # Blue
                        symbol = '▼'
                    else:
                        front_type = 'warm'
                        color = '#FF0000'  # Red
                        symbol = '▲'
                    
                    fronts.append({
                        'type': front_type,
                        'lat': (p1['lat'] + p2['lat']) / 2,
                        'lon': (p1['lon'] + p2['lon']) / 2,
                        'color': color,
                        'symbol': symbol,
                        'gradient': gradient,
                        'temp_diff': temp_diff
                    })
        
        print(f"✅ Found {len(fronts)} weather fronts")
        return fronts
    
    def calculate_front_velocity(self, grid_data: List[Dict]) -> Dict:
        """
        Calculate average front movement velocity and direction
        
        Args:
            grid_data: List of weather grid points with forecasts
            
        Returns:
            Dict with velocity and direction
        """
        # Use pressure trend as proxy for front movement
        avg_pressure_trend = np.mean([p['pressure_trend'] for p in grid_data])
        avg_wind_speed = np.mean([p['wind_speed'] for p in grid_data])
        avg_wind_dir = np.mean([p['wind_direction'] for p in grid_data])
        
        return {
            'velocity_ms': avg_wind_speed * 0.5,  # Fronts move ~50% of wind speed
            'direction_deg': avg_wind_dir,
            'pressure_trend': avg_pressure_trend
        }
    
    def get_wind_arrow(self, direction_deg: float) -> str:
        """
        Get Unicode arrow for wind direction
        
        Args:
            direction_deg: Wind direction in degrees (0=N, 90=E, etc.)
            
        Returns:
            Unicode arrow character
        """
        # Normalize to 0-360
        direction_deg = direction_deg % 360
        
        # Map to 8 cardinal directions
        if 337.5 <= direction_deg or direction_deg < 22.5:
            return self.SYMBOLS['arrow_n']
        elif 22.5 <= direction_deg < 67.5:
            return self.SYMBOLS['arrow_ne']
        elif 67.5 <= direction_deg < 112.5:
            return self.SYMBOLS['arrow_e']
        elif 112.5 <= direction_deg < 157.5:
            return self.SYMBOLS['arrow_se']
        elif 157.5 <= direction_deg < 202.5:
            return self.SYMBOLS['arrow_s']
        elif 202.5 <= direction_deg < 247.5:
            return self.SYMBOLS['arrow_sw']
        elif 247.5 <= direction_deg < 292.5:
            return self.SYMBOLS['arrow_w']
        else:
            return self.SYMBOLS['arrow_nw']
    
    def get_weather_symbol(self, weather_code: int) -> str:
        """Get weather symbol for WMO code"""
        if weather_code == 0:
            return self.SYMBOLS['sun']
        elif weather_code in [1, 2, 3]:
            return self.SYMBOLS['cloud']
        elif weather_code in [45, 48]:
            return self.SYMBOLS['fog']
        elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            return self.SYMBOLS['rain']
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            return self.SYMBOLS['snow']
        elif weather_code in [95, 96, 99]:
            return self.SYMBOLS['storm']
        else:
            return self.SYMBOLS['cloud']
    
    def add_fronts_to_map(self, folium_map, grid_data: List[Dict], systems: List[Dict], fronts: List[Dict]):
        """
        Add weather fronts and systems to Folium map using newspaper-style symbols
        
        Args:
            folium_map: Folium map object
            grid_data: Weather grid data
            systems: Pressure systems
            fronts: Weather fronts
        """
        print("🎨 Adding weather symbols to map...")
        
        # Add pressure systems (H/L markers)
        for system in systems:
            color = '#FF0000' if system['type'] == 'high' else '#0000FF'
            
            folium.Marker(
                location=[system['lat'], system['lon']],
                icon=folium.DivIcon(html=f"""
                    <div style="font-size: 48px; font-weight: bold; color: {color}; 
                                text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, 
                                -2px 2px 0 #fff, 2px 2px 0 #fff, 
                                0 0 8px #fff, 0 0 12px #fff;">
                        {system['symbol']}
                    </div>
                """),
                tooltip=f"{system['type'].upper()}: {system['pressure']:.1f} hPa"
            ).add_to(folium_map)
        
        # Add weather fronts (lines with symbols)
        for front in fronts:
            folium.CircleMarker(
                location=[front['lat'], front['lon']],
                radius=12,
                popup=f"{front['type'].title()} Front: {front['temp_diff']:.1f}°C change",
                tooltip=f"{front['type'].title()} Front {front['symbol']}",
                color=front['color'],
                fill=True,
                fillColor=front['color'],
                fillOpacity=0.8,
                weight=5
            ).add_to(folium_map)
        
        # Add wind arrows at key points
        wind_points = grid_data[::2]  # Sample every other point
        for point in wind_points:
            arrow = self.get_wind_arrow(point['wind_direction'])
            weather_sym = self.get_weather_symbol(point['weather_code'])
            
            folium.Marker(
                location=[point['lat'], point['lon']],
                icon=folium.DivIcon(html=f"""
                    <div style="font-size: 32px; text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, 
                                -2px 2px 0 #fff, 2px 2px 0 #fff, 
                                0 0 8px #fff, 0 0 12px #fff;">
                        {weather_sym}{arrow}
                    </div>
                """),
                tooltip=f"{point['wind_speed']:.1f} m/s {arrow} | {point['temperature']:.0f}°C"
            ).add_to(folium_map)
        
        print(f"✅ Added {len(systems)} pressure systems, {len(fronts)} fronts, {len(wind_points)} wind arrows")


def main():
    """Test weather front tracker"""
    print("=" * 80)
    print("🌀 WEATHER FRONT TRACKER")
    print("=" * 80)
    print()
    
    tracker = WeatherFrontTracker()
    
    # Define UK bounds
    uk_bounds = {
        'north': 59.0,
        'south': 49.5,
        'west': -8.0,
        'east': 2.0
    }
    
    # Get grid weather data
    grid_data = tracker.get_grid_weather(uk_bounds, grid_size=6)
    
    # Detect systems and fronts
    systems = tracker.detect_pressure_systems(grid_data)
    fronts = tracker.detect_fronts(grid_data)
    
    # Calculate front movement
    movement = tracker.calculate_front_velocity(grid_data)
    
    print(f"\n📊 Front Movement:")
    print(f"   Velocity: {movement['velocity_ms']:.1f} m/s")
    print(f"   Direction: {movement['direction_deg']:.0f}° {tracker.get_wind_arrow(movement['direction_deg'])}")
    print(f"   Pressure Trend: {movement['pressure_trend']:+.1f} hPa/3h")
    
    # Create map
    m = folium.Map(location=[54.5, -2.5], zoom_start=6)
    tracker.add_fronts_to_map(m, grid_data, systems, fronts)
    
    # Save
    m.save('weather_fronts_map.html')
    print(f"\n💾 Saved: weather_fronts_map.html")
    print("✅ Complete!")


if __name__ == '__main__':
    main()

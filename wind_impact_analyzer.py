#!/usr/bin/env python3
"""
Wind Farm Impact Analyzer
Identifies operational impacts from weather forecasts
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

class WindImpactAnalyzer:
    """Analyze weather impacts on wind turbine operations"""
    
    # Typical offshore wind turbine operational thresholds
    CUT_IN_SPEED = 3.5  # m/s - minimum wind for generation
    RATED_SPEED = 12.5  # m/s - optimal generation (nameplate capacity)
    CUT_OUT_SPEED = 25.0  # m/s - emergency shutdown
    ICING_TEMP = 0.0  # °C - freezing point
    ICING_HUMIDITY = 80  # % - high humidity threshold for icing risk
    
    def __init__(self):
        """Initialize impact analyzer"""
        pass
    
    def analyze_current_conditions(self, weather: Dict) -> Dict:
        """
        Analyze current weather conditions
        
        Args:
            weather: Current weather dict with wind_speed_ms, temperature_c, etc.
            
        Returns:
            Dict with operational status and impact details
        """
        wind_speed = weather['wind_speed_ms']
        wind_gust = weather['wind_gust_ms']
        temp = weather['temperature_c']
        humidity = weather['humidity_pct']
        
        status = {
            'timestamp': weather['timestamp'],
            'operational': True,
            'capacity_factor': 1.0,
            'status': 'normal',
            'color': 'green',
            'issues': []
        }
        
        # Check for cut-out conditions (too windy)
        if wind_gust >= self.CUT_OUT_SPEED or wind_speed >= self.CUT_OUT_SPEED:
            status['operational'] = False
            status['capacity_factor'] = 0.0
            status['status'] = 'shutdown'
            status['color'] = 'red'
            status['issues'].append({
                'type': 'cut_out',
                'severity': 'critical',
                'description': f'High winds: {wind_speed:.1f} m/s (gusts {wind_gust:.1f} m/s) - Emergency shutdown',
                'wind_speed': wind_speed
            })
        
        # Check for cut-in conditions (too little wind)
        elif wind_speed < self.CUT_IN_SPEED:
            status['operational'] = True  # Turbine running but not generating
            status['capacity_factor'] = 0.0
            status['status'] = 'idle'
            status['color'] = 'yellow'
            status['issues'].append({
                'type': 'cut_in',
                'severity': 'low',
                'description': f'Low wind: {wind_speed:.1f} m/s - No generation',
                'wind_speed': wind_speed
            })
        
        # Check for sub-optimal wind
        elif wind_speed < self.RATED_SPEED:
            capacity_factor = self._estimate_capacity_factor(wind_speed)
            status['capacity_factor'] = capacity_factor
            status['status'] = 'sub_optimal'
            status['color'] = 'yellow'
            status['issues'].append({
                'type': 'sub_optimal',
                'severity': 'low',
                'description': f'Below rated speed: {wind_speed:.1f} m/s - {capacity_factor*100:.0f}% capacity',
                'wind_speed': wind_speed,
                'capacity_factor': capacity_factor
            })
        
        # Check for icing risk
        if temp <= self.ICING_TEMP and humidity >= self.ICING_HUMIDITY:
            status['issues'].append({
                'type': 'icing',
                'severity': 'medium',
                'description': f'Icing risk: {temp:.1f}°C @ {humidity}% humidity',
                'temperature': temp,
                'humidity': humidity
            })
            if status['color'] == 'green':
                status['color'] = 'orange'
                status['status'] = 'icing_risk'
        
        return status
    
    def analyze_forecast(self, forecast: List[Dict], current_time: Optional[datetime] = None) -> List[Dict]:
        """
        Analyze forecast data for upcoming impacts
        
        Args:
            forecast: List of hourly forecast dicts
            current_time: Reference time (default: now)
            
        Returns:
            List of impact events with timing
        """
        if current_time is None:
            current_time = datetime.now()
        
        events = []
        in_event = False
        event_start = None
        event_type = None
        
        for hour in forecast:
            hour_status = self.analyze_current_conditions(hour)
            
            # Detect start of impact event
            if not in_event and hour_status['issues']:
                in_event = True
                event_start = hour['timestamp']
                event_type = hour_status['issues'][0]['type']
                event_severity = hour_status['issues'][0]['severity']
                event_description = hour_status['issues'][0]['description']
            
            # Detect end of impact event
            elif in_event and not hour_status['issues']:
                eta = (event_start - current_time).total_seconds() / 3600  # hours
                duration = (hour['timestamp'] - event_start).total_seconds() / 3600
                
                events.append({
                    'type': event_type,
                    'severity': event_severity,
                    'start_time': event_start,
                    'end_time': hour['timestamp'],
                    'eta_hours': max(0, eta),
                    'duration_hours': duration,
                    'description': event_description,
                    'status': 'upcoming' if eta > 0 else 'current'
                })
                
                in_event = False
        
        # Handle event that extends beyond forecast window
        if in_event:
            eta = (event_start - current_time).total_seconds() / 3600
            events.append({
                'type': event_type,
                'severity': event_severity,
                'start_time': event_start,
                'end_time': None,  # Extends beyond forecast
                'eta_hours': max(0, eta),
                'duration_hours': None,
                'description': event_description,
                'status': 'upcoming' if eta > 0 else 'current'
            })
        
        return events
    
    def get_overall_status(self, current_status: Dict, events: List[Dict]) -> Dict:
        """
        Determine overall operational status considering current + forecast
        
        Args:
            current_status: Current conditions status
            events: List of forecast events
            
        Returns:
            Dict with overall status and priority issues
        """
        # Start with current status
        overall = {
            'current': current_status,
            'upcoming_events': events,
            'priority_color': current_status['color'],
            'priority_issue': current_status['issues'][0] if current_status['issues'] else None
        }
        
        # Check for critical upcoming events
        for event in events:
            if event['severity'] == 'critical' and event['eta_hours'] < 24:
                overall['priority_color'] = 'red'
                overall['priority_issue'] = {
                    'type': event['type'],
                    'severity': event['severity'],
                    'description': f"⚠️ {event['description']} (ETA: {event['eta_hours']:.1f}h)"
                }
                break
            elif event['severity'] == 'medium' and event['eta_hours'] < 12:
                if overall['priority_color'] != 'red':
                    overall['priority_color'] = 'orange'
                    overall['priority_issue'] = {
                        'type': event['type'],
                        'severity': event['severity'],
                        'description': f"⚠️ {event['description']} (ETA: {event['eta_hours']:.1f}h)"
                    }
        
        return overall
    
    def _estimate_capacity_factor(self, wind_speed: float) -> float:
        """
        Estimate turbine capacity factor based on wind speed
        Uses simplified power curve approximation
        
        Args:
            wind_speed: Wind speed in m/s
            
        Returns:
            Capacity factor (0.0 to 1.0)
        """
        if wind_speed < self.CUT_IN_SPEED:
            return 0.0
        elif wind_speed >= self.RATED_SPEED:
            return 1.0
        else:
            # Cubic relationship between cut-in and rated speed
            normalized = (wind_speed - self.CUT_IN_SPEED) / (self.RATED_SPEED - self.CUT_IN_SPEED)
            return normalized ** 3
    
    def format_impact_summary(self, wind_farm: Dict, analysis: Dict) -> str:
        """
        Format human-readable impact summary
        
        Args:
            wind_farm: Wind farm data with name, capacity
            analysis: Overall status analysis
            
        Returns:
            Formatted string summary
        """
        lines = []
        lines.append(f"🏭 {wind_farm['name']} ({wind_farm['capacity_mw']} MW)")
        lines.append(f"   Status: {analysis['current']['status'].upper()}")
        lines.append(f"   Capacity: {analysis['current']['capacity_factor']*100:.0f}%")
        
        if analysis['priority_issue']:
            lines.append(f"   ⚠️  {analysis['priority_issue']['description']}")
        
        if analysis['upcoming_events']:
            lines.append(f"   📅 {len(analysis['upcoming_events'])} upcoming event(s)")
            for event in analysis['upcoming_events'][:3]:  # Show first 3
                if event['eta_hours'] > 0:
                    lines.append(f"      - {event['type']}: ETA {event['eta_hours']:.1f}h, duration {event['duration_hours']:.1f}h" if event['duration_hours'] else f"      - {event['type']}: ETA {event['eta_hours']:.1f}h")
        
        return '\n'.join(lines)


def main():
    """Test the impact analyzer"""
    import json
    from weather_fetcher import WeatherFetcher
    
    print("=" * 80)
    print("⚡ WIND FARM IMPACT ANALYZER")
    print("=" * 80)
    print()
    
    # Fetch weather data
    fetcher = WeatherFetcher()
    weather_data = fetcher.fetch_all_wind_farms(
        'geojson_exports/offshore_wind_farms.geojson',
        include_forecast=True,
        include_marine=False
    )
    
    # Analyze impacts
    analyzer = WindImpactAnalyzer()
    
    print("\n" + "=" * 80)
    print("📊 IMPACT ANALYSIS")
    print("=" * 80)
    
    for farm in weather_data:
        if 'current' not in farm or 'forecast' not in farm:
            continue
        
        # Analyze current conditions
        current_status = analyzer.analyze_current_conditions(farm['current'])
        
        # Analyze forecast
        events = analyzer.analyze_forecast(farm['forecast'])
        
        # Get overall status
        overall = analyzer.get_overall_status(current_status, events)
        
        # Print summary
        print("\n" + analyzer.format_impact_summary(farm, overall))
    
    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()

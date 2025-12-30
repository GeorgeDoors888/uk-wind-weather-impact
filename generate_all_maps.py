#!/usr/bin/env python3
"""
Generate multiple specialized map views
"""

import json
import os
from weather_wind_impact_map import generate_weather_impact_map, capture_screenshot, MAP_CONFIG

def generate_all_map_variants():
    """Generate different map variants and save them"""
    
    variants = [
        {
            'name': 'full_weather_impact',
            'config': {
                'show_dnos': True,
                'show_gsps': False,
                'show_wind': True,
                'show_weather_impacts': True,
                'show_weather_fronts': True,
                'show_interconnectors': True,
                'center': [54.5, -2.5],
                'zoom': 6.5
            },
            'description': 'Full map with weather, wind farms, DNOs, and interconnectors'
        },
        {
            'name': 'interconnectors_only',
            'config': {
                'show_dnos': False,
                'show_gsps': False,
                'show_wind': False,
                'show_weather_impacts': False,
                'show_weather_fronts': False,
                'show_interconnectors': True,
                'center': [54.0, -1.0],
                'zoom': 5.5
            },
            'description': 'Interconnectors only - power links to Europe'
        },
        {
            'name': 'dno_boundaries',
            'config': {
                'show_dnos': True,
                'show_gsps': False,
                'show_wind': False,
                'show_weather_impacts': False,
                'show_weather_fronts': False,
                'show_interconnectors': False,
                'center': [54.5, -2.5],
                'zoom': 6.0
            },
            'description': 'DNO boundaries only'
        },
        {
            'name': 'gsp_boundaries',
            'config': {
                'show_dnos': False,
                'show_gsps': True,
                'show_wind': False,
                'show_weather_impacts': False,
                'show_weather_fronts': False,
                'show_interconnectors': False,
                'center': [54.5, -2.5],
                'zoom': 6.5
            },
            'description': 'GSP boundaries only'
        },
        {
            'name': 'wind_farms_weather',
            'config': {
                'show_dnos': False,
                'show_gsps': False,
                'show_wind': True,
                'show_weather_impacts': True,
                'show_weather_fronts': True,
                'show_interconnectors': False,
                'center': [54.5, -1.5],
                'zoom': 6.5
            },
            'description': 'Wind farms with weather impacts'
        },
        {
            'name': 'interconnectors_and_wind',
            'config': {
                'show_dnos': False,
                'show_gsps': False,
                'show_wind': True,
                'show_weather_impacts': True,
                'show_weather_fronts': False,
                'show_interconnectors': True,
                'center': [54.0, -1.0],
                'zoom': 6.0
            },
            'description': 'Power generation and transmission - wind farms and interconnectors'
        },
        {
            'name': 'network_overview',
            'config': {
                'show_dnos': True,
                'show_gsps': True,
                'show_wind': True,
                'show_weather_impacts': False,
                'show_weather_fronts': False,
                'show_interconnectors': True,
                'center': [54.5, -2.5],
                'zoom': 6.0
            },
            'description': 'Complete network: DNOs, GSPs, wind farms, interconnectors'
        }
    ]
    
    print("=" * 80)
    print("🗺️  GENERATING MAP VARIANTS")
    print("=" * 80)
    print()
    
    results = []
    
    for i, variant in enumerate(variants, 1):
        print(f"\n[{i}/{len(variants)}] Generating: {variant['name']}")
        print(f"    Description: {variant['description']}")
        
        # Update global config
        MAP_CONFIG.update(variant['config'])
        
        # Generate map
        html_file, impact_results = generate_weather_impact_map()
        
        # Rename files
        variant_html = f"map_{variant['name']}.html"
        variant_png = f"map_{variant['name']}.png"
        
        os.rename(html_file, variant_html)
        os.rename('weather_impact_map.png', variant_png)
        
        print(f"    ✅ Saved: {variant_html}")
        print(f"    ✅ Saved: {variant_png}")
        
        results.append({
            'name': variant['name'],
            'description': variant['description'],
            'html': variant_html,
            'png': variant_png
        })
    
    # Save index
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    for result in results:
        print(f"\n{result['name']}:")
        print(f"  Description: {result['description']}")
        print(f"  HTML: {result['html']}")
        print(f"  PNG:  {result['png']}")
    
    # Create index HTML
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UK Energy Maps - Index</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #2c3e50; }
            .map-card { 
                background: white; 
                padding: 20px; 
                margin: 20px 0; 
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .map-card h2 { color: #3498db; margin-top: 0; }
            .map-card p { color: #7f8c8d; }
            .map-card a { 
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 10px 0 0;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            .map-card a:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <h1>🗺️ UK Energy Maps</h1>
        <p>Generated: """ + str(os.popen('date').read().strip()) + """</p>
    """
    
    for result in results:
        index_html += f"""
        <div class="map-card">
            <h2>{result['name'].replace('_', ' ').title()}</h2>
            <p>{result['description']}</p>
            <a href="{result['html']}" target="_blank">View Interactive Map</a>
            <a href="{result['png']}" target="_blank">View PNG</a>
        </div>
        """
    
    index_html += """
    </body>
    </html>
    """
    
    with open('map_index.html', 'w') as f:
        f.write(index_html)
    
    print("\n✅ Created map_index.html")
    print("\n🌐 Open map_index.html to browse all maps")
    
    return results


if __name__ == '__main__':
    generate_all_map_variants()

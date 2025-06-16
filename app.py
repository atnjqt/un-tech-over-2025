# I want a simple Flask app to serve a dashboard for displaying geopandas visualizations

from flask import Flask, render_template, request, jsonify, url_for

# the main route 

from gigaspatial.config import config
from gigaspatial.handlers import OSMLocationFetcher
import geopandas as gpd
import os

### Not needed with pip install - path to giga-spatial if you cloned it and are going to extend it
# sys.path.append("path_to_giga_spatial/")
###
from dotenv import load_dotenv
load_dotenv()

# Setup Flask app with static folder
app = Flask(__name__, 
           static_folder='static',
           static_url_path='/static')
app.config.from_object(config)
@app.route('/')
def index():
    return render_template('index.html')


# a dashboard route for OSM data - this loads the initial page without data
@app.route('/dashboard', methods=['GET'])
def dashboard():
    # List of country codes with names
    country_data = [
        {'code': 'RWA', 'name': 'Rwanda 🇷🇼'},
        {'code': 'SYR', 'name': 'Syria 🇸🇾'},
        {'code': 'SGP', 'name': 'Singapore 🇸🇬'},
        {'code': 'UGA', 'name': 'Uganda 🇺🇬'},
        {'code': 'BRB', 'name': 'Barbados 🇧🇧'},
        {'code': 'BLZ', 'name': 'Belize 🇧🇿'},
        {'code': 'HT', 'name': 'Haiti 🇭🇹'},
        {'code': 'PS', 'name': 'Palestine 🇵🇸'},
        {'code': 'USA', 'name': 'United States 🇺🇸'},
        {'code': 'KEN', 'name': 'Kenya 🇰🇪'},
        {'code': 'GBR', 'name': 'United Kingdom 🇬🇧'},
    ]
    
    # Keep a list of just the codes for backend processing
    country_codes = [country['code'] for country in country_data]
    
    # All available location types
    all_location_types = {
        "amenity": ["school", "hospital", "restaurant", "bank", "cafe", "pharmacy", "post_office"],
        "building": ["residential", "commercial", "industrial", "retail", "office"],
        "waterway": ["river", "canal", "stream", "lake"],
        "emergency": ["fire_station", "police", "ambulance"],
        "natural": ["forest", "park", "beach", "wetland"],
        "transportation": ["bus_stop", "train_station", "airport", "ferry_terminal"],
        "tourism": ["hotel", "museum", "attraction", "viewpoint"],
        "historic": ["monument", "ruins", "castle", "memorial"],
        "leisure": ["playground", "sports_centre", "swimming_pool", "golf_course"],
        "shop": ["supermarket", "convenience_store", "clothing_store", "electronics_store"],
        "landuse": ["residential", "commercial", "industrial", "retail", "agricultural"],
        "boundary": ["administrative", "national_park", "nature_reserve"],
        "power": ["substation", "transformer", "power_line"],
        "healthcare": ["clinic", "health_center", "pharmacy"],
        "waste": ["recycling", "landfill", "waste_disposal"],
        "sport": ["stadium", "gym", "sports_field", "tennis_court"],
        "finance": ["atm", "bank", "insurance", "investment"],
        "cultural": ["theatre", "cinema", "library", "art_gallery"],
        "religion": ["church", "mosque", "temple", "synagogue"],
        "education": ["university", "college", "school", "kindergarten"],
        "public": ["post_office", "community_centre", "civic_building", "government_office"],
        "miscellaneous": ["fountain", "clock", "statue", "sculpture"]
    }
    
    # Get selected types from previous request, if any
    selected_types = request.args.getlist('location_types')
    if not selected_types:
        selected_types = ['amenity']
    
    return render_template('dashboard.html', 
                          map_html=None,
                          country_data=country_data,
                          country_codes=country_codes, 
                          all_location_types=all_location_types,
                          selected_types=selected_types,
                          request=request)


# An API endpoint to fetch map data
@app.route('/api/fetch-map-data', methods=['POST'])
def fetch_map_data():
    data = request.json
    country = data.get('country', 'RWA')
    selected_types = data.get('location_types', ['amenity'])
    
    # All available location types
    all_location_types = {
        "amenity": ["school", "hospital", "restaurant", "bank", "cafe", "pharmacy", "post_office"],
        "building": ["residential", "commercial", "industrial", "retail", "office"],
        "waterway": ["river", "canal", "stream", "lake"],
        "emergency": ["fire_station", "police", "ambulance"],
        "natural": ["forest", "park", "beach", "wetland"],
        "transportation": ["bus_stop", "train_station", "airport", "ferry_terminal"],
        "tourism": ["hotel", "museum", "attraction", "viewpoint"],
        "historic": ["monument", "ruins", "castle", "memorial"],
        "leisure": ["playground", "sports_centre", "swimming_pool", "golf_course"],
        "shop": ["supermarket", "convenience_store", "clothing_store", "electronics_store"],
        "landuse": ["residential", "commercial", "industrial", "retail", "agricultural"],
        "boundary": ["administrative", "national_park", "nature_reserve"],
        "power": ["substation", "transformer", "power_line"],
        "healthcare": ["clinic", "health_center", "pharmacy"],
        "waste": ["recycling", "landfill", "waste_disposal"],
        "sport": ["stadium", "gym", "sports_field", "tennis_court"],
        "finance": ["atm", "bank", "insurance", "investment"],
        "cultural": ["theatre", "cinema", "library", "art_gallery"],
        "religion": ["church", "mosque", "temple", "synagogue"],
        "education": ["university", "college", "school", "kindergarten"],
        "public": ["post_office", "community_centre", "civic_building", "government_office"],
        "miscellaneous": ["fountain", "clock", "statue", "sculpture"]
    }
    
    # Filter the location_types dictionary to only include selected types
    location_types = {k: v for k, v in all_location_types.items() if k in selected_types}
    
    # If no valid types selected, default to waterway
    if not location_types:
        location_types = {"waterway": all_location_types["waterway"]}
    
    try:
        fetcher = OSMLocationFetcher(country=country, location_types=location_types)
        df = fetcher.fetch_locations()
        if not isinstance(df, gpd.GeoDataFrame):
            gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        else:
            gdf = df
            
        # Generate interactive map HTML
        map_html = gdf.explore(column="category")._repr_html_()
        
        return jsonify({
            'status': 'success',
            'map_html': map_html
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
# I want a simple Flask app to serve a dashboard for displaying geopandas visualizations

from flask import Flask, render_template, request, jsonify, url_for

# the main route 

from gigaspatial.config import config
from gigaspatial.handlers import OSMLocationFetcher
from gigaspatial.handlers import AdminBoundaries
from gigaspatial.generators import GeometryBasedZonalViewGenerator

import geopandas as gpd
import os
import folium
import logging

logger = logging.getLogger(__name__)
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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

# a dashboard route for OSM data - this loads the initial page without data
@app.route('/dashboard', methods=['GET'])
def dashboard():
    # List of country codes with names
    country_data = [
        {'code': 'RWA', 'name': 'Rwanda 🇷🇼'},
        {'code': 'UGA', 'name': 'Uganda 🇺🇬'},
        {'code': 'KEN', 'name': 'Kenya 🇰🇪'},
        {'code': 'HT', 'name':  'Haiti 🇭🇹'},
        {'code': 'VEN', 'name': 'Venezuela 🇻🇪'},
        {'code': 'COL', 'name': 'Colombia 🇨🇴'},
        {'code': 'USA', 'name': 'United States 🇺🇸'},
        {'code': 'GBR', 'name': 'United Kingdom 🇬🇧'},
        {'code': 'DEU', 'name': 'Germany 🇩🇪'},
        {'code': 'UKR', 'name': 'Ukraine 🇺🇦'},
        {'code': 'PS', 'name': 'Palestine 🇵🇸'},
        {'code': 'IRN', 'name': 'Iran 🇮🇷'},
        {'code': 'TUR', 'name': 'Turkiye 🇹🇷'},
        {'code': 'SYR', 'name': 'Syria 🇸🇾'},
        {'code': 'SSD', 'name': 'South Sudan 🇸🇸'},
        {'code': 'AFG', 'name': 'Afghanistan 🇦🇫'}
    ]
    
    # Keep a list of just the codes for backend processing
    country_codes = [country['code'] for country in country_data]
    
    # All available location types
    # https://wiki.openstreetmap.org/wiki/Map_features
    all_location_types = {
        "amenity": ["school", "hospital", "restaurant", "bank", "cafe", "pharmacy", "post_office", "social_facility"],
        "building": ["residential", "commercial", "industrial", "retail", "office"],
        "waterway": ["river", "canal", "stream", "lake"],
        "emergency": ["fire_station", "police", "ambulance"],
        "natural": ["forest", "park", "beach", "wetland", "coastline"],
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
    try:
        # Verify we have valid JSON data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
            
        data = request.json
        country = data.get('country', 'RWA')
        selected_types = data.get('location_types', ['amenity'])
        
        print(f"Processing request for country: {country}, types: {selected_types}")
        
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
            
        print(f"Using location types: {location_types}")
        
        # Initialize OSM fetcher
        fetcher = OSMLocationFetcher(country=country, location_types=location_types)
        
        # Fetch OSM data
        print(f"Fetching OSM data...")
        df = fetcher.fetch_locations()
        
        # Check if data is empty
        if df is None or df.empty:
            return jsonify({
                'status': 'warning',
                'message': f'No locations found for {country} with selected types'
            }), 200
        
        print(f"OSM data fetched successfully. Shape: {df.shape}")
        
        # Convert to GeoDataFrame if needed
        if not isinstance(df, gpd.GeoDataFrame):
            print("Converting to GeoDataFrame...")
            # Check if we have the geometry column
            if 'geometry' not in df.columns:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing geometry column. Available columns: {list(df.columns)}'
                }), 500
                
            gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        else:
            gdf = df
            
        # Generate interactive map HTML
        print("Generating map...")
        map_html = gdf.explore(column="category")._repr_html_()
        
        return jsonify({
            'status': 'success',
            'map_html': map_html,
            'data_count': len(gdf),
            'types_found': list(gdf['category'].unique()) if 'category' in gdf.columns else []
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in fetch-map-data: {str(e)}\n{error_details}")
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'details': error_details
        }), 500

# The unhcr.ipynb notebook saves the data file here relative to the project root.
UNHCR_DATA_PATH = os.path.join(os.path.dirname(__file__), ".", "data", "unhcr", "camps.geojson")

def get_available_countries():
    """Reads the UNHCR data and returns a list of countries (iso3 codes) that have camps."""
    try:
        if not os.path.exists(UNHCR_DATA_PATH):
            logger.error(f"UNHCR data file not found at {UNHCR_DATA_PATH}. Please run the unhcr.ipynb notebook first to download the data.")
            return []
        gdf = gpd.read_file(UNHCR_DATA_PATH)
        # Get unique 'iso3' country codes and sort them.
        countries = sorted(gdf['iso3'].unique().tolist())
        return countries
    except Exception as e:
        logger.error(f"Error reading UNHCR data file: {e}")
        return []
    
@app.route('/dashboard2', methods=['GET'])
def index2():
    """Renders the home page with a dropdown of countries."""
    countries = get_available_countries()
    return render_template('unchr-map.html', countries=countries)

@app.route('/map', methods=['POST'])
def generate_map():
    """Generates and displays the map for the selected country."""
    selected_country = request.form.get('country')
    if not selected_country:
        return "Please select a country.", 400

    logger.info(f"Generating map for {selected_country}")

    try:
        # Load administrative boundaries for the selected country (level 1)
        logger.info("Loading administrative boundaries...")
        admin_boundaries = AdminBoundaries.create(country_code=selected_country, admin_level=1)
        admin_gdf = admin_boundaries.to_geodataframe()
        logger.info("Administrative boundaries loaded.")

        # Load the global UNHCR camps data
        logger.info("Loading UNHCR camps data...")
        camps_gdf = gpd.read_file(UNHCR_DATA_PATH)
        logger.info("UNHCR camps data loaded.")

        # Filter camps for the selected country and ensure CRS matches
        country_camps_gdf = camps_gdf[camps_gdf['iso3'] == selected_country].copy()
        country_camps_gdf = country_camps_gdf.to_crs(admin_gdf.crs)
        
        # Create a zonal view generator using the admin boundaries
        logger.info("Creating zonal view generator...")
        view_gen = GeometryBasedZonalViewGenerator(
            zone_data=admin_gdf,
            zone_id_column="id",
            zone_data_crs=admin_gdf.crs
        )

        # Map the number of camps to each administrative zone
        logger.info("Mapping camp counts...")
        camp_counts = view_gen.map_points(country_camps_gdf)
        view_gen.zone_gdf["camp_count"] = view_gen.zone_gdf.index.map(camp_counts).fillna(0)
        logger.info("Camp counts mapped.")

        # Create the interactive map
        logger.info("Creating map visualization...")
        
        # Create a base map centered on the country
        m = view_gen.zone_gdf.explore(
            'camp_count',
            legend=True,
            cmap='viridis',
            tooltip=['name', 'camp_count'],
            popup=True,
            legend_kwds={'caption': f'UNHCR Camps in {selected_country}'}
        )

        # Overlay the exact camp locations if any exist
        if not country_camps_gdf.empty:
            country_camps_gdf.explore(
                m=m,
                color='red',
                marker_kwds={'radius': 5},
                tooltip=['gis_name'], # Show camp name on hover
                name='UNHCR Camp Locations'
            )
        
        folium.LayerControl().add_to(m)
        logger.info("Map created.")

        # Render the map to an HTML string and pass it to the template
        map_html = m._repr_html_()
        return render_template('map.html', map_html=map_html, country=selected_country)

    except Exception as e:
        logger.error(f"An error occurred while generating the map for {selected_country}: {e}", exc_info=True)
        # This can happen if GADM data is not available for a country/level.
        error_message = f"Could not generate map for {selected_country}. The administrative boundaries might not be available from the data source. Full error: {e}"
        return render_template('error.html', error_message=error_message)


# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
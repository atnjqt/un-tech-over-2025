/**
 * Dashboard app.js - Main JavaScript for the Geospatial Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle select/deselect all buttons for location types
    initializeFilterButtons();
    
    // Initialize load data button
    initializeLoadDataButton();
});

/**
 * Initializes filter buttons functionality
 */
function initializeFilterButtons() {
    const selectAllBtn = document.getElementById('selectAll');
    const deselectAllBtn = document.getElementById('deselectAll');
    const checkboxes = document.getElementsByClassName('location-checkbox');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            for (let checkbox of checkboxes) {
                checkbox.checked = true;
            }
        });
    }
    
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            for (let checkbox of checkboxes) {
                checkbox.checked = false;
            }
        });
    }
}

/**
 * Initialize the load data button to fetch map data via AJAX
 */
function initializeLoadDataButton() {
    const loadBtn = document.getElementById('loadDataBtn');
    if (!loadBtn) return;
    
    loadBtn.addEventListener('click', function() {
        loadMapData();
    });
}

/**
 * Load map data via AJAX POST request
 */
function loadMapData() {
    // Show loading indicator
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'flex';
    }
    
    // Get selected country
    const countrySelect = document.getElementById('country');
    const country = countrySelect ? countrySelect.value : 'RWA';
    
    // Get country name from the select option text
    const countryName = countrySelect ? countrySelect.options[countrySelect.selectedIndex].text : 'Rwanda';
    
    // Get selected location types
    const locationCheckboxes = document.getElementsByClassName('location-checkbox');
    const selectedTypes = [];
    for (let checkbox of locationCheckboxes) {
        if (checkbox.checked) {
            selectedTypes.push(checkbox.value);
        }
    }
    
    // Prepare data for API request
    const data = {
        country: country,
        location_types: selectedTypes.length > 0 ? selectedTypes : ['amenity']
    };
    
    // Make AJAX request
    fetch('/api/fetch-map-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Update map container with new map HTML
            const mapContainer = document.querySelector('.map-container');
            if (mapContainer) {
                mapContainer.innerHTML = data.map_html;
            }
            
            // Update selection info display
            updateSelectionInfo(countryName, country, selectedTypes);
        } else {
            console.error('Error loading map data:', data.message);
            alert('Error loading map data: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error loading map data:', error);
        alert('Error loading map data. Please try again.');
    })
    .finally(() => {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    });
}

/**
 * Update the selection info display with current filter values
 */
function updateSelectionInfo(countryName, countryCode, locationTypes) {
    const infoPanel = document.getElementById('currentSelectionInfo');
    const countryNameElement = document.getElementById('selectedCountryName');
    const countryCodeElement = document.getElementById('selectedCountryCode');
    const locationTypesElement = document.getElementById('selectedLocationTypes');
    
    if (infoPanel && countryNameElement && countryCodeElement && locationTypesElement) {
        // Format location types as a comma-separated list with title case
        const formattedTypes = locationTypes.map(type => {
            return type.charAt(0).toUpperCase() + type.slice(1);
        }).join(', ');
        
        // Update display elements
        countryNameElement.textContent = countryName;
        countryCodeElement.textContent = countryCode;
        locationTypesElement.textContent = formattedTypes || 'None';
        
        // Show the info panel
        infoPanel.style.display = 'block';
    }
}

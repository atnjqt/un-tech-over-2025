/**
 * Dashboard app.js - Main JavaScript for the Geospatial Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle select/deselect all buttons for location types
    initializeFilterButtons();
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

document.addEventListener('DOMContentLoaded', function() {
    updateElementFromAPI('indoor_humidity', '/api/fan/indoor_humidity');
    updateElementFromAPI('outdoor_humidity', '/api/fan/outdoor_humidity');
    updateElementFromAPI('fan_speed', '/api/fan/speed');
    updateElementFromAPI('battery_voltage', '/api/battery/voltage');
    updateElementFromAPI('light_brightness', '/api/light/brightness');
    updateElementFromAPI('light_state', '/api/light/state');
    updateElementFromAPI('motion_state', '/api/motion/state');
    updateElementFromAPI('mac_address', '/api/wlan/mac');
});

/**
 * Fetches data from a specified API endpoint and updates the text content of an HTML element.
 * 
 * @param {string} elementId The ID of the HTML element to update.
 * @param {string} apiEndpoint The relative URL of the API endpoint to query for data.
 * @param {string} datasuffix The string in the element's current text content that should be prefixed with the fetched data.
 */
function updateElementFromAPI(elementId, apiEndpoint) {
    fetch(apiEndpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const element = document.getElementById(elementId);

            if (element) {
                element.textContent = data;
            }
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}

function setLightState(state) {
    const url = '/api/light/state';
    
    fetch(url, {
        method: 'PUT',
        headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `state=${state}`
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        console.log(data);
        updateElementFromAPI('light_state', '/api/light/state');
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
    });
}
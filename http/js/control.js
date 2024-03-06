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
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
    });
}
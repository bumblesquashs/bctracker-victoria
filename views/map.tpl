
% include('templates/header', title='System Map', include_maps=True)

% fleetnums = list(map(lambda b: int(b.fleetnum), rtbuslist))
% scheduleds = list(map(lambda b: 1 if b.scheduled else 0, rtbuslist))
% lats = list(map(lambda b: b.lat, rtbuslist))
% lons = list(map(lambda b: b.lon, rtbuslist))

<h1>System Map</h1>

% include('templates/footer')

<div id="system-map"></div>
<script>
    mapboxgl.accessToken = ''; // Replace with proper token in production and when testing - DO NOT COMMIT!
    var map = new mapboxgl.Map({
      container: 'system-map',
      center: [-123.538, 48.52],
      zoom: 9,
      style: 'mapbox://styles/mapbox/streets-v11'
    });

    map.setStyle('mapbox://styles/mapbox/light-v10')

    const fleetnums = {{ fleetnums }}
    const scheduleds = {{ scheduleds }}
    const lats = {{ lats }}
    const lons = {{ lons }}
    for (var i = 0; i < fleetnums.length; i++) {
        var marker = document.createElement('div');
        marker.className = 'marker';
        if (!scheduleds[i]) {
            marker.style.backgroundColor = '#aaaaaa'
        }
        fleetnum = fleetnums[i]
        if (fleetnum == 100000) {
            fleetnum = 'Unknown Bus'
        }
        marker.innerHTML = '<img src="/img/busicon.png" /><span>' + fleetnum + '</span>'
    
        new mapboxgl.Marker(marker).setLngLat([lons[i], lats[i]]).addTo(map);
    }
</script>

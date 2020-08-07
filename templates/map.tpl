<div id="map"></div>
<script>
    const lat = parseFloat("{{lat}}");
    const lon = parseFloat("{{lon}}");

    mapboxgl.accessToken = ''; // Replace with proper token in production and when testing - DO NOT COMMIT!
    var map = new mapboxgl.Map({
      container: 'map',
      center: [lon, lat],
      zoom: 14,
      style: 'mapbox://styles/mapbox/streets-v11',
      interactive: false
    });

    var marker = document.createElement('div');
    marker.className = 'marker';

    new mapboxgl.Marker(marker).setLngLat([lon, lat]).addTo(map);

    map.setStyle('mapbox://styles/mapbox/light-v10')
</script>
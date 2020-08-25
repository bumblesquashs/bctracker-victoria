% import datastructure as ds
% import web

<div id="map"></div>
<script>
    const lat = parseFloat("{{lat}}");
    const lon = parseFloat("{{lon}}");

    mapboxgl.accessToken = '{{web.mapbox_api_key}}';
    var map = new mapboxgl.Map({
      container: 'map',
      center: [lon, lat],
      zoom: 14,
      style: 'mapbox://styles/mapbox/streets-v11',
      interactive: false
    });

    map.setStyle('mapbox://styles/mapbox/light-v10')
</script>

% if defined('marker_type'):
    % if marker_type == 'bus':
      <script>
        var marker = document.createElement('div');
        marker.className = 'marker';
        marker.innerHTML = '<img src="/img/busicon.png" />'

        new mapboxgl.Marker(marker).setLngLat([lon, lat]).addTo(map);
      </script>
    % elif marker_type == 'stop':
      <script>
        var marker = document.createElement('div');
        marker.className = 'marker';
        marker.innerHTML = '<img src="/img/stopicon.png" />'

        new mapboxgl.Marker(marker).setLngLat([lon, lat]).addTo(map);
      </script>
    % end
% end

% if defined('shape_id'):
  % points = filter(lambda p: p.shape_id == shape_id, ds.all_points)
  % sorted_points = sorted(points, key=lambda p: int(p.sequence))
  % coords = list(map(lambda p: [float(p.lon), float(p.lat)], sorted_points))
  <script>
    const coords = {{ coords }}

    map.on('load', function() {
      map.addSource('route', {
        'type': 'geojson',
        'data': {
          'type': 'Feature',
          'properties': {},
          'geometry': {
            'type': 'LineString',
            'coordinates': coords
          }
        }
      });
      map.addLayer({
        'id': 'route',
        'type': 'line',
        'source': 'route',
        'layout': {
          'line-join': 'round',
          'line-cap': 'round'
        },
        'paint': {
          'line-color': '#4040FF',
          'line-width': 4
        }
      });
    });
  </script>
% end

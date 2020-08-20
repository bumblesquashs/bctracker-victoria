% include('templates/header', title=stop.name, include_maps=True)

<h1>{{ stop.name }}</h1>
<h2>Bus Stop {{ stop.number }}</h2>
<hr />

% include('templates/map', lon=stop.lon, lat=stop.lat)

% for service in sorted(stop.services):
  % stop_times = [stop_time for stop_time in stop.stop_times if stop_time.trip.service == service]
  <h2>{{ service }}</h2>
  <p>{{ len(stop_times) }} Trips</p>

  <table class="pure-table pure-table-horizontal pure-table-striped">
    <thead>
      <tr>
        <th>Time</th>
        <th>Headsign</th>
        <th class="desktop-only">Block</th>
        <th>Trip</th>
      </tr>
    </thead>
    <tbody>
      % last_hour = -1
      % for stop_time in sorted(stop_times):
        % this_hour = int(stop_time.time.split(':')[0])
        % if last_hour == -1:
          % last_hour = this_hour
        % elif this_hour > last_hour:
          <tr>
            <td class="desktop-only" colspan="4"><hr /></td>
            <td class="mobile-only" colspan="3"><hr /></td>
          </tr>
          % last_hour = this_hour
        % end
        <tr>
          <td>{{ stop_time.time }}</td>
          <td>{{ stop_time.trip.headsign }}</td>
          <td class="desktop-only"><a href="/blocks/{{ stop_time.trip.block.block_id }}">{{ stop_time.trip.block.block_id }}</a></td>
          <td><a href="/trips/{{ stop_time.trip.trip_id }}">{{ stop_time.trip.trip_id }}</a></td>
        </tr>
      % end
    </tbody>
  </table>
% end

% include('templates/footer')

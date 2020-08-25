% from bus import BusStatus
% from bus_history import get_history
% from bus_realtime import get_update_time
% from formatting import format_date, format_date_mobile

% include('templates/header', title=f'Bus {bus}', include_maps=True)

<h1>Bus {{ bus }}</h1>
<h2>{{ bus.range }} </h2>
<hr />

% if bus.status == BusStatus.NOT_TRACKING:
  <h2>{{ bus }} is not active right now</h2>
  <p>Last updated {{ get_update_time() }}</p>
% elif bus.status == BusStatus.NOT_IN_SERVICE:
  % include('templates/map', lat=bus.lat, lon=bus.lon, marker_type='bus')

  <h2>{{ bus }} is active, but not assigned to any route</h2>
  <p>Last updated {{ get_update_time() }}</p>
% elif bus.status == BusStatus.IN_SERVICE:
  % trip = bus.realtime.trip

  % include('templates/map', lat=bus.lat, lon=bus.lon, marker_type='bus')

  <h2>{{ trip.headsign }}</h2>
  <p>Last updated {{ get_update_time() }}</p>

  % if bus.realtime.at_stop:
    <p>Current Stop: <a href="/stops/{{bus.realtime.stop.number}}">{{ bus.realtime.stop }}</a></p>
  % else:
    <p>Current Stop: Unavailable</p>
  % end
  <p>
    <a href="/routes/{{trip.route.number}}">View Route</a><br />
    <a href="/blocks/{{trip.block_id}}">View Block</a><br />
    <a href="/trips/{{trip.trip_id}}">View Trip</a>
  </p>
% end

<h2>Service History</h2>

% (last_seen, block_history) = get_history(bus.bus_id)

% if last_seen == '':
  <p>No history for this vehicle found</p>
  <p>This site began tracking data on May 5th 2020, so vehicles retired before then will not show any history</p>
% else:
  <p>Last seen {{ format_date(last_seen) }}</p>
% end

% if len(block_history) > 0:
  <p>For entries made under a older GTFS version, the block may no longer be valid</p>
  <table class="pure-table pure-table-horizontal pure-table-striped">
    <thead>
      <tr>
        <th>Date</th>
        <th>Assigned Block</th>
        <th class="desktop-only">Assigned Routes</th>
        <th class="desktop-only">Time of Day</th>
        <th class="mobile-only">Time</th>
      </tr>
    </thead>
    <tbody>
      % for history in block_history:
        <tr>
          <td>
            <span class="desktop-only">{{ format_date(history.date) }}</span>
            <span class="mobile-only no-wrap">{{ format_date_mobile(history.date) }}</span>
          </td>
          <td>
            <a href="/blocks/{{history.block_id}}">{{ history.block_id }}</a>
            <span class="mobile-only smaller-font">
              <br />
              {{ history.routes_string }}
            </span>
          </td>
          <td class="desktop-only">{{ history.routes_string }}</td>
          <td class="no-wrap"></td>
        </tr>
      % end
    </tbody>
  </table>
% end

% include('templates/footer')

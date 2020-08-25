% from formatting import format_time

% if len(stop_entries) > 0:
  <h2 id="{{day}}">{{ day }}</h2>
  <p>{{ len(stop_entries) }} Trips</p>
  
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
      % for stop_entry in stop_entries:
        % this_hour = int(stop_entry.stoptime.split(':')[0])
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
          <td>{{ format_time(stop_entry.stoptime) }}</td>
          <td>{{ stop_entry.trip.headsign }}</td>
          <td class="desktop-only"><a href="/blocks/{{ stop_entry.trip.blockid }}">{{ stop_entry.trip.blockid }}</a></td>
          <td><a href="/trips/{{ stop_entry.tripid }}">{{ stop_entry.tripid }}</a></td>
        </tr>
      % end
    </tbody>
  </table>
% end
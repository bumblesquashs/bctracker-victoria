% import datastructure as ds
% from formatting import format_time

<table class="pure-table pure-table-horizontal pure-table-striped">
  <thead>
    <tr>
      <th class="desktop-only">Start Time</th>
      <th class="mobile-only">Start</th>
      <th>Headsign</th>
      <th class="desktop-only">Departing From</th>
      <th class="desktop-only">Block</th>
      <th>Trip</th>
    </tr>
  </thead>

  <tbody>
    % for trip in sorted(trips):
      <tr>
        <td>{{ trip.stop_times[0].time }}</td>
        <td>{{ trip.headsign }}</td>
        <td class="desktop-only"><a href="/stops/{{trip.stop_times[0].stop.number}}">{{ trip.stop_times[0].stop.name }}</a></td>
        <td class="desktop-only"><a href="/blocks/{{trip.block.block_id}}">{{ trip.block.block_id }}</a></td>
        <td><a href="/trips/{{trip.trip_id}}">{{ trip.trip_id }}</a></td>
      </tr>
    % end
  </tbody>
</table>

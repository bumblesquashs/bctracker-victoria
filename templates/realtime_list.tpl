% if defined('group_name'):
  <h2>{{ group_name }}</h2>
% end

<table class="pure-table pure-table-horizontal pure-table-striped fixed-table">
  <thead>
    <tr>
      <th class="desktop-only">Fleet Number</th>
      <th class="desktop-only">Year and Model</th>
      <th class="mobile-only">Bus</th>
      <th>Headsign</th>
      <th class="desktop-only">Current Block</th>
      <th class="desktop-only">Current Trip</th>
      <th class="desktop-only">Current Stop</th>
    </tr>
  </thead>
  <tbody>
    % for bus in sorted(buses):
      <tr>
        % if bus.number == -1:
          <td>Unknown Bus</td>
          <td class="desktop-only"></td>
        % else:
          <td>
            <a href="/bus/{{bus.number}}">{{ bus }}</a>
            <span class="mobile-only smaller-font">
              <br />
              {{ bus.range }}
            </span>
          </td>
          <td class="desktop-only">{{ bus.range }}</td>
        % end

        % if bus.status == BusStatus.IN_SERVICE:
          <td>{{ bus.realtime.trip.headsign }}</td>
          <td class="desktop-only"><a href="/blocks/{{bus.realtime.trip.block_id}}">{{ bus.realtime.trip.block_id }}</a></td>
          <td class="desktop-only"><a href="/trips/{{bus.realtime.trip_id}}">{{ bus.realtime.trip_id }}</a></td>
          % if bus.realtime.at_stop:
            <td class="desktop-only"><a href="/stops/{{bus.realtime.stop.number}}">{{ bus.realtime.stop.name }}</a></td>
          % else:
            <td class="desktop-only">Unavailable</td>
          % end
        % elif bus.status == BusStatus.NOT_IN_SERVICE:
          <td>Not in service</td>
          <td class="desktop-only"></td>
          <td class="desktop-only"></td>
          <td class="desktop-only"></td>
        %end
      </tr>
    %end
  </tbody>
</table>

% import realtime as rt
% import businfotable as businfo
% import history as hist
% from formatting import format_date, format_date_mobile

% include('templates/header', title='Vehicle History')

<h1>Vehicle History</h1>
<hr />

<h2>Last Block Assigned</h2>
<p>For entries made under a older GTFS version, the block may no longer be valid</p>
<table class="pure-table pure-table-horizontal pure-table-striped">
  <thead>
    <tr>
      <th class="desktop-only">Fleet Number</th>
      <th class="desktop-only">Year and Model</th>
      <th class="desktop-only">Date Last Assigned</th>
      <th class="desktop-only">Assigned Block</th>
      <th class="desktop-only">Assigned Routes</th>
      
      <th class="mobile-only">Bus</th>
      <th class="mobile-only">Date</th>
      <th class="mobile-only">Block</th>
    </tr>
  </thead>
  <tbody>
    % last_seen = hist.get_last_seen()
    % last_blocks = last_seen['last_blocks']
    % last_block_keys = list(last_blocks.keys())
    % last_block_keys.sort(key = lambda x: int(x))

    % last_times = last_seen['last_times']
    % last_times_keys = list(last_times.keys())
    % last_times_keys.sort(key = lambda x: int(x))
    % for fleetnum in last_block_keys:
      % if (fleetnum == '0'):
        % continue
      % end
      % obj = last_blocks[fleetnum]
      % busrange = businfo.get_bus_range(fleetnum)
      <tr>
        <td>
          <a href="/bus/{{fleetnum}}">{{ fleetnum }}</a>
          <span class="mobile-only smaller-font">
            <br />
            {{ busrange.year }} {{ busrange.model }}
          </span>
        </td>
        <td class="desktop-only">{{ busrange.year }} {{ busrange.model }}</td>
        <td>
          <span class="desktop-only">{{ format_date(obj['day']) }}</span>
          <span class="mobile-only no-wrap">{{ format_date_mobile(obj['day']) }}</span>
        </td>
        <td><a href="/blocks/{{obj['blockid']}}">{{ obj['blockid'] }}</a></td>
        <td class="desktop-only">{{ ', '.join(sorted(obj['routes'])) }}</td>
      </tr>
    % end
  </tbody>
</table>

<h2>Last Time Tracked</h2>
<p>The last time the vehicle was detected by the tracker even if it wasn't assigned to a route</p>
<table class="pure-table pure-table-horizontal pure-table-striped">
  <thead>
    <tr>
      <th class="desktop-only">Fleet Number</th>
      <th class="desktop-only">Year and Model</th>
      <th class="desktop-only">Date Last Assigned</th>
      
      <th class="mobile-only">Bus</th>
      <th class="mobile-only">Date</th>
    </tr>
  </thead>
  <tbody>
    % for fleetnum in last_times_keys:
      % if (fleetnum == '0'):
        % continue
      % end
      % date = last_times[fleetnum]['day']
      % busrange = businfo.get_bus_range(fleetnum)
      <tr>
        <td>
          <a href="/bus/{{fleetnum}}">{{ fleetnum }}</a>
          <span class="mobile-only smaller-font">
            <br />
            {{ busrange.year }} {{ busrange.model }}
          </span>
        </td>
        <td class="desktop-only">{{ busrange.year }} {{ busrange.model }}</td>
        <td>
          <span class="desktop-only">{{ format_date(date) }}</span>
          <span class="mobile-only no-wrap">{{ format_date_mobile(date) }}</span>
        </td>
      </tr>
    % end
  </tbody>
</table>

% include('templates/footer')

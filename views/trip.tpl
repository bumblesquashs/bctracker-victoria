% include('templates/header', title=str(trip))

<h1>{{ trip }}</h1>
<h2>Trip {{ trip.trip_id }} ({{ trip.service }})</h2>
<hr />

<p>
  <a href="/routes/{{trip.route.number}}">View Route</a>
  <br />
  <a href="/blocks/{{trip.block.block_id}}">View Block</a>
</p>

<p>Number of stops: {{ len(trip.stop_times) }}</p>

<table class="pure-table pure-table-horizontal pure-table-striped">
  <thead>
    <tr>
      <th>Time</th>
      <th class="desktop-only">Stop Code</th>
      <th class="desktop-only">Stop Name</th>
      <th class="mobile-only">Stop</th>
    </tr>
  </thead>
  <tbody>
    % for stop_time in sorted(trip.stop_times):
      <tr>
        <td>{{ stop_time.time }}</td>
        <td>
          <a href="/stops/{{stop_time.stop.number}}">{{ stop_time.stop.number }}</a>
          <span class="mobile-only smaller-font">
            <br />
            {{ stop_time.stop.name }}
          </span>
        </td>
        <td class="desktop-only">{{ stop_time.stop.name }}</td>
      </tr>
    % end
  </tbody>
</table>

% include('templates/footer')

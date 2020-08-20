% include('templates/header', title='All Blocks')

<h1>All Blocks</h1>
<hr />

<table class="pure-table pure-table-horizontal pure-table-striped">
  <thead>
    <tr>
      <th class="desktop-only">Block</th>
      <th class="desktop-only">Routes</th>
      <th class="desktop-only">Start Time</th>
      <th class="desktop-only">Service Days</th>

      <th class="mobile-only">Block and Routes</th>
      <th class="mobile-only">Start</th>
      <th class="mobile-only">Days</th>
    </tr>
  </thead>
  <tbody>
    % for block in sorted(blocks):
      <tr>
        <td>
          <a href="blocks/{{block.block_id}}">{{ block.block_id }}</a>
          <span class="mobile-only smaller-font">
            <br />
            {{ block.routes_string }}
          </span>
        </td>
        <td class="desktop-only">{{ block.routes_string }}</td>
        <td>{{ block.start_time }}</td>
        <td class="no-wrap">{{ block.service }}</td>
      </tr>
    % end
  </tbody>
</table>

% include('templates/footer')

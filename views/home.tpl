% include('templates/header', title='BCTracker - Victoria')

<h1>BCTracker - Victoria</h1>
<h2>Welcome to the BCTracker site for the Victoria Regional Transit System!</h2>
<hr />

<h2>Quick Search</h2>

<script type="text/javascript">
  function busSearch() {
    window.location = "/bus/" + document.getElementById('bus_id_search').value;
  }

  function routeSearch() {
    window.location = "/routes/" + document.getElementById('route_id_search').value;
  }

  function stopSearch() {
    window.location = "/stops/" + document.getElementById('stop_id_search').value;
  }
</script>

<form onsubmit="busSearch()" action="javascript:void(0)">
  <label for="bus_id_search">Fleet Number:</label>
  <br />
  <input type="text" id="bus_id_search" name="bus_id" method="post">
  <input type="submit" value="Search" class="button">
</form>

<form onsubmit="routeSearch()" action="javascript:void(0)">
  <label for="route_id_search">Route Number:</label>
  <br />
  <input type="text" id="route_id_search" name="route_id" method="post">
  <input type="submit" value="Search" class="button">
</form>

<form onsubmit="stopSearch()" action="javascript:void(0)">
  <label for="stop_id_search">Stop Number:</label>
  <br />
  <input type="text" id="stop_id_search" name="stop_id" method="post">
  <input type="submit" value="Search" class="button">
</form>

<h2>All Routes</h2>

<table class="pure-table pure-table-horizontal pure-table-striped">
    <thead>
        <tr>
            <th>Route</th>
        </tr>
    </thead>
    <tbody>
        % for route in sorted(routes):
            <tr>
                <td><a href="routes/{{route.number}}">{{ route }}</a></td>
            </tr>
        % end
    </tbody>
</table>

% include('templates/footer')

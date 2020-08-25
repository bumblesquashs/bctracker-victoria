% from bus import BusStatus
% from bus_realtime import get_update_time

% include('templates/header', title='Realtime')

<h1>Realtime</h1>
% if group == 'all':
  <h2>All active buses</h2>
% elif group == 'route':
  <h2>Routes with active buses</h2>
% elif group == 'model':
  <h2>Models with active buses</h2>
% end
<hr />

<div class="mobile-only">
  <div class="flexbox-space-between">
    % if group == 'all':
      <span class="button button-disabled">All Buses</span>
    % else:
      <a class="button" href="/realtime">All Buses</a>
    % end

    % if group == 'route':
      <span class="button button-disabled">By Route</span>
    % else:
      <a class="button" href="?group=route">By Route</a>
    % end

    % if group == 'model':
      <span class="button button-disabled">By Model</span>
    % else:
      <a class="button" href="?group=model">By Model</a>
    % end
  </div>
  <div class="horizontal-line"></div>
</div>
<p>
  <span class="desktop-only">
    % if group == 'all':
      <span class="button button-disabled">All Buses</span>
    % else:
      <a class="button" href="/realtime">All Buses</a>
    % end

    % if group == 'route':
      <span class="button button-disabled">By Route</span>
    % else:
      <a class="button" href="?group=route">By Route</a>
    % end

    % if group == 'model':
      <span class="button button-disabled">By Model</span>
    % else:
      <a class="button" href="?group=model">By Model</a>
    % end
    <span class="vertical-line"></span>
  </span>
  <span>
    % if group == 'all':
    <a class="button" href="?rt=reload">Refresh Realtime</a>
    % elif group == 'route':
    <a class="button" href="?group=route&rt=reload">Refresh Realtime</a>
    % elif group == 'model':
    <a class="button" href="?group=model&rt=reload">Refresh Realtime</a>
    % end
  </span>
</p>
<p>Last updated {{ get_update_time() }}</p>

% if len(buses) == 0:
  <p>There doesn't appear to be any buses out right now. Victoria has no nightbus service, so this should be the case overnight. If you look out your window and the sun is shining, there may be an issue with the GTFS getting up-to-date info.</p>
% else:
  <%
    if group == 'all':
      include('templates/realtime_list', buses=buses)
    elif group == 'route':
      buses_on_route = [bus for bus in buses if bus.status == BusStatus.IN_SERVICE]
      routes = set(map(lambda b: b.realtime.trip.route, buses_on_route))
      for route in sorted(routes):
        route_buses = [bus for bus in buses_on_route if bus.realtime.trip.route == route]
        include('templates/realtime_list', group_name=str(route), buses=route_buses)
      end

      buses_off_route = [bus for bus in buses if bus.status == BusStatus.NOT_IN_SERVICE]
      if len(buses_off_route) > 0:
        include('templates/realtime_list', group_name='Not in service', buses=buses_off_route)
      end
    elif group == 'model':
      models = set(map(lambda b: b.range.model, buses))
      for model in sorted(models):
        model_buses = [bus for bus in buses if bus.range.model == model]
        include('templates/realtime_list', group_name=model, buses=model_buses, show_model=False)
      end
    end
  %>
% end

% include('templates/footer')

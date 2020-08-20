% from trip import Direction

% include('templates/header', title=str(route))

<h1>{{ route }}</h1>
<hr />

% for service in sorted(route.services):
  % trips = [trip for trip in route.trips if trip.service == service]

  <h2>{{ service }}</h2>

  % outbound_trips = [trip for trip in trips if trip.direction == Direction.OUTBOUND]
  % if len(outbound_trips) > 0:
    <p>Outbound - {{ len(outbound_trips) }} trips</p>

    % include('templates/triplist', trips=outbound_trips)
  % end

  % inbound_trips = [trip for trip in trips if trip.direction == Direction.INBOUND]
  % if len(inbound_trips) > 0:
    <p>Inbound - {{ len(inbound_trips) }} trips</p>

    % include('templates/triplist', trips=inbound_trips)
  % end
% end

% include('templates/footer')

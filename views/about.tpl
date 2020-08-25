% include('templates/header', title='About')

<h1>About</h1>
<hr />

<p>
  BCTracker is a browser for the <a href="https://developers.google.com/transit/gtfs">GTFS</a> static and realtime data provided by the Greater Victoria Transit System operated by <a href="https://bctransit.com/victoria">BC Transit</a>.
  The data is presented here for the use of whoever is interested, with the goal of making it easier to browse schedules and track down buses.
<p>

<p>
  The website (both the pages and the data processing code) is written in python using a simple web framework called Bottle.
  The code can be found on <a href="https://github.com/bumblesquashs/bctracker-victoria">GitHub</a> if you are interested in seeing how it works or trying to run it yourself.
</p>

<p>
  If you are curious about BCTracker, have questions, or something seems broken, contact us by emailing <a href="mailto:james@bctracker.ca">james@bctracker.ca</a>
</p>

<br />
<i> - James & Perrin, 2020 </i>

% include('templates/footer')

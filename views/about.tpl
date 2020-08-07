% include('templates/header', title='About')

<h1>About</h1>
<hr />

This simple site is a browser for the <a href="https://developers.google.com/transit/gtfs">GTFS</a> static data provided by the Greater Victoria Transit System operated by BC Transit. <br>

<p>
It also loads in realtime data following the gtfs-realtime specification, which is viewable on the Realtime page. The data is presented here for the use of whoever is interested. Hopefully it should make browsing schedules and tracking down busses easier.
Let me know if you find it useful!
<p>

<p>
BC Transit provides the nextride site already, but this site is to browse information not present there - block data, view all vehicles etc. However,
that nextride site has an API (which I use to steal the fleetid->fleetnumber translation) which might have better realtime bus data - one thing I might do
is take realtime data from that API instead of the gtfs realtime at some point.
</p>

<p>
The site (both the pages and the data processing code) is written in python using a dead simple web framework called Bottle - the code for
the site is on github <a href="https://github.com/bumblesquashs/bctracker-victoria">here</a>. Fair warning - the code is pretty gross right now and sorta gremlin like... don't judge too hard! If you run into issues running it, let me know.
</p>

<p>
If you are otherwise curious about this, have questions, or something seems broken, contact bumblesquash somehow;
(such as on the T-Comm discord or by email at tracker@bumblesquash.com).
</p>

<br />
<i> - Bumblesquash, 2020 </i>

% include('templates/footer')
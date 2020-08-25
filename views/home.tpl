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

<h2>Latest Updates</h2>
<div class="home-update">
  <div class="home-update-header">
    <h3>New Website Look</h3>
    August 21, 2020
  </div>
  <div class="home-update-content">
    <p>
      BCTracker has a new look!
      We've been working hard to get this updated design ready, and there's a lot of new things for you to enjoy - including full mobile support, improved realtime navigation, maps, and much more.
    </p>
    <p>
      We've also moved the website to a new address at <a href="http://bctracker.ca">bctracker.ca</a>.
      The old URL will continue to be usable for a while, but if you've bookmarked any pages you'll want to make sure they're updated.
    </p>
    <p>
      Over the next few weeks we'll be making more changes to the systems that make the website work behind the scenes.
      You (hopefully) won't notice any differences, but it will allow us to add lots more new and exciting stuff in the future.
      We're always looking for ways to improve the website even more, and your feedback is always welcome.
      Send us an email anytime at <a href="mailto:james@bctracker.ca">james@bctracker.ca</a>
    </p>
    Enjoy!
  </div>
</div>

% include('templates/footer')

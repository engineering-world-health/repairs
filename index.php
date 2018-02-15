<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<!--<meta http-equiv='refresh' content='1'>-->
<link rel='stylesheet' href='css/style.css'>
<link rel="icon" href="img/icon.ico"></link>
</head>
<body>
  <div class='panel-outer full-width'>
    <div class='panel-inner'>
      <h1>EWH Repair Database</h1>
      <par>
        <a href='http://www.ewh.org/' target='_blank'>Engineering World Health</a>
        is a global organization which supports medical technology in the developing world.
        Every year, as part of the EWH Summer Institute,
        students from around the world travel to low-resource countries
        to work alongside local technicians repairing medical equipment.
        Each repair is logged and classified to help understand common challenges in these contexts.
        <br><br>
        Below is an interactive summary of the repairs from
        Nicaragua, Rwanda, and Tanzania,
        from 2011 to 2015.
      </par>
    </div>
  </div>
  <div class='panel-row'>
    <div class='panel-outer full-width'>
      <div class='panel-inner'>
        <div id='filters'>
          <div class='dropdown-container'>
            <h5>Year</h5>
            <select class=dropdown id='select-year'></select>
          </div>
          <div class='dropdown-container'>
            <h5>Country</h5>
            <select class=dropdown id='select-country'></select>
          </div>
          <div class='dropdown-container'>
            <h5>Equipment Type</h5>
            <select class=dropdown id='select-equipment'></select>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div id='loading'>
    <div class='panel-outer full-width'>
      <div class='panel-inner'>
        <div id='spinner'></div>
      </div>
    </div>
  </div>
  <div id='render' style='display: none'>
    <div class='panel-row'>
      <div class='panel-outer half-width'>
        <div class='panel-inner'>
          <h2>Repair Result</h2>
          <div id='repair-result'></div>
        </div>
      </div><!--
    --><div class='panel-outer half-width'>
        <div class='panel-inner'>
          <h2>Repair Type</h2>
          <div id='repair-fix'></div>
        </div>
      </div>
    </div>
    <div class='panel-row'>
      <div class='panel-outer full-width'>
        <div class='panel-inner'>
          <h2>Equipment Type</h2>
          <div id='repair-equipment'></div>
        </div>
      </div>
    </div>
    <div class='panel-row'>
      <div class='panel-outer full-width'>
        <div class='panel-inner'>
          <h2>Summary</h2>
          <div id='checkbox-table'></div>
          <div id='repair-table'></div>
        </div>
      </div>
    </div>
  </div>
</body>
<script src='https://d3js.org/d3.v4.min.js'></script>
<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script src='https://cdnjs.cloudflare.com/ajax/libs/spin.js/2.0.1/spin.min.js'></script>
<script src='js/main.js'></script>
</script>
</html>

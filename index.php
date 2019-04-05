<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<!--<meta http-equiv='refresh' content='1'>-->
<link rel="icon" href="img/icon.ico"></link>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<link rel='stylesheet' href='css/style.css'>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
<title>EWH Repair Database</title>
</head>
<body>
  <div class='container'>
    <div class='row'>
      <div class='pane col-12'>
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
        several countries over the past few years.
        Source code can be found on
        <a href='https://github.com/jessexknight/ewh-repairs' target='_blank'>Github</a>.
        </par>
      </div>
    </div>
    <div class='row' style='display:block'>
      <div class='pane col-12'>
        <div class='row'>
          <div id='filters'></div>
          <div class='col-xs-6 col-sm-4 col-md-3 col-lg-3'>
            <h4>Matching Repairs:</h4>
            <span id='num-matches'>0</span><!--
         --><a id='download'>Download CSV</a>
          </div>
        </div>
      </div>
    </div>
    <div class='row' id='loading' style='display:block'>
      <div class='pane col-12'>
        <div id='spinner'></div>
      </div>
    </div>
    <div id='render' style='display: none'>
      <div class='row'>
        <div class='pane col-sx-12 col-sm-6'>
          <h2>Repair Result</h2>
          <div id='repair-result'></div>
        </div>
        <div class='pane col-sx-12 col-sm-6'>
          <h2>Repair Type</h2>
          <div id='repair-fix'></div>
        </div>
      </div>
      <div class='row'>
        <div class='pane col-12'>
          <h2>Equipment Type</h2>
          <div id='repair-equipment'></div>
        </div>
      </div>
      <div class='row'>
        <div class='pane col-12'>
          <h2>Summary</h2>
          <div class='row' id='checkbox-table'></div>
          <div id='repair-table'></div>
        </div></div>
      </div>
    </div>
  </div>
</body>
<script src='https://d3js.org/d3.v4.min.js'></script>
<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script src='https://cdnjs.cloudflare.com/ajax/libs/spin.js/2.0.1/spin.min.js'></script>
<script src='js/main.js'></script>
<script src='js/jquery.tablesorter.min.js'></script>
</script>
</html>

<?php
$f = fopen('data.csv','r');
$data = [];
$rowas = [];
$header = fgetcsv($f,0,',','"');
while ($row = fgetcsv($f,0,',','"')) {
  foreach ($row as $k=>$v) {
    $rowas[$header[$k]] = $v;
  }
  $data[] = $rowas;
}
echo json_encode($data);
?>

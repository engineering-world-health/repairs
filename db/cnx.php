<?php
// from sql --------------------------------------------------------------------
// $sql = json_decode(file_get_contents('sql.json'));
// $cnx = $sql->cnx;
// $mysqli = new mysqli($cnx->host, $cnx->user, $cnx->pass);
// $mysqli->select_db($cnx->db);
// $result = $mysqli->query("SELECT * FROM `".$sql->tables->repairs."`");
// $data = [];
// while($row = mysqli_fetch_assoc($result)){
//   $data[] = $row;
// }
// from local csv --------------------------------------------------------------
$f = fopen('../database.csv','r');
$data = [];
$rowas = [];
$header = fgetcsv($f,0,',','"');
while ($row = fgetcsv($f,0,',','"')) {
  foreach ($row as $k=>$v) {
    $rowas[$header[$k]] = $v;
  }
  $data[] = $rowas;
}
// json encode regardless ------------------------------------------------------
echo json_encode($data);
?>

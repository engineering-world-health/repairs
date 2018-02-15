<?php
$sql = json_decode(file_get_contents('sql.json'));
$cnx = $sql->cnx;
$mysqli = new mysqli($cnx->host, $cnx->user, $cnx->pass);
$mysqli->select_db($cnx->db);
$result = $mysqli->query("SELECT * FROM `".$sql->tables->repairs."`");
$data = [];
while($row = mysqli_fetch_assoc($result)){
  $data[] = $row;
}
echo json_encode($data);
$mysqli->close();
?>

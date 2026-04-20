<?php
// Kontrollpark — angelegten Code wieder loeschen (Fehler/Tippfehler beheben)
// GET ?code=KP-XXXX  oder ?klasse=XXX (alle einer Klasse)
// Header X-Teacher-Key muss TEACHER_KEY entsprechen
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

$code   = trim($_GET['code'] ?? '');
$klasse = strtoupper(trim($_GET['klasse'] ?? ''));

try {
  $db = getDB();
  if($code){
    $stmt = $db->prepare('DELETE FROM km_kp_students WHERE student_code=?');
    $stmt->execute([$code]);
  } elseif($klasse){
    $stmt = $db->prepare('DELETE FROM km_kp_students WHERE class_code=?');
    $stmt->execute([$klasse]);
  } else {
    echo json_encode(['ok'=>false,'error'=>'Parameter code oder klasse erforderlich']);
    exit;
  }
  echo json_encode(['ok'=>true,'deleted'=>$stmt->rowCount()]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

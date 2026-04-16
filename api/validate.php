<?php
require_once 'config.php';
cors();

$body = json_decode(file_get_contents('php://input'), true);
$code = strtoupper(trim($body['code'] ?? ''));

if(!$code){ echo json_encode(['valid'=>false,'error'=>'Kein Code angegeben']); exit; }

try {
  $db = getDB();
  $stmt = $db->prepare('SELECT code, class_name FROM km_codes WHERE code=? AND active=1');
  $stmt->execute([$code]);
  $row = $stmt->fetch();

  if($row){
    // Progress-Eintrag anlegen falls noch nicht vorhanden
    $db->prepare('INSERT IGNORE INTO km_progress (code, class_name) VALUES (?, ?)')->execute([$code, $row['class_name']]);
    echo json_encode(['valid'=>true, 'code'=>$row['code'], 'class'=>$row['class_name']]);
  } else {
    echo json_encode(['valid'=>false, 'error'=>'Code ungültig oder nicht aktiv']);
  }
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['valid'=>false,'error'=>'Datenbankfehler']);
}

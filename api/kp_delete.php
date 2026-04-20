<?php
// Kontrollpark — Lehrer-Endpunkt: Submission(s) loeschen
// DELETE /api/kp_delete.php?id=NN         loescht einen Eintrag
// DELETE /api/kp_delete.php?klasse=XXX    loescht alle einer Klasse (Vorsicht!)
// Header X-Teacher-Key muss TEACHER_KEY entsprechen
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

$id     = intval($_GET['id'] ?? 0);
$klasse = strtoupper(trim($_GET['klasse'] ?? ''));

if(!$id && !$klasse){
  echo json_encode(['ok'=>false,'error'=>'Parameter id oder klasse erforderlich']);
  exit;
}

try {
  $db = getDB();
  if($id){
    $stmt = $db->prepare('DELETE FROM km_kp_submissions WHERE id=?');
    $stmt->execute([$id]);
  } else {
    $stmt = $db->prepare('DELETE FROM km_kp_submissions WHERE class_code=?');
    $stmt->execute([$klasse]);
  }
  echo json_encode(['ok'=>true, 'deleted'=>$stmt->rowCount()]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

<?php
require_once 'config.php';
cors();

if(!rateLimit('sync', 60)){
  http_response_code(429);
  echo json_encode(['ok'=>false,'error'=>'Zu viele Syncs']);
  exit;
}

$body = json_decode(file_get_contents('php://input'), true) ?: [];
$code    = strtoupper(trim($body['code']     ?? ''));
$missions= is_array($body['missions'] ?? null) ? $body['missions'] : [];
$xp      = max(0, min(intval($body['xp'] ?? 0), 1000000));
$streak  = max(0, min(intval($body['streak'] ?? 0), 10000));
$mastery = is_array($body['mastery'] ?? null) ? $body['mastery'] : [];
$errors  = is_array($body['errors']  ?? null) ? $body['errors']  : [];

if(!$code || !preg_match('/^[A-Z0-9]{4,20}$/', $code)){
  echo json_encode(['ok'=>false,'error'=>'Ungültiger Code']); exit;
}

$missionsJson = json_encode($missions);
$masteryJson  = json_encode($mastery);
$errorsJson   = json_encode($errors);
if(strlen($missionsJson) > 60000 || strlen($masteryJson) > 60000 || strlen($errorsJson) > 60000){
  echo json_encode(['ok'=>false,'error'=>'Datenblock zu groß']); exit;
}

try {
  $db = getDB();

  // Prüfen ob Code existiert und aktiv ist
  $stmt = $db->prepare('SELECT code FROM km_codes WHERE code=? AND active=1');
  $stmt->execute([$code]);
  if(!$stmt->fetch()){ echo json_encode(['ok'=>false,'error'=>'Code ungültig']); exit; }

  // Upsert progress
  $stmt = $db->prepare('
    INSERT INTO km_progress (code, missions, xp, streak, mastery, errors, last_active)
    VALUES (?, ?, ?, ?, ?, ?, NOW())
    ON DUPLICATE KEY UPDATE
      missions    = VALUES(missions),
      xp          = VALUES(xp),
      streak      = VALUES(streak),
      mastery     = VALUES(mastery),
      errors      = VALUES(errors),
      last_active = NOW()
  ');
  $stmt->execute([$code, $missionsJson, $xp, $streak, $masteryJson, $errorsJson]);

  echo json_encode(['ok'=>true]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

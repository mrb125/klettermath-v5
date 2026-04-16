<?php
require_once 'config.php';
cors();

$body = json_decode(file_get_contents('php://input'), true);
$code    = strtoupper(trim($body['code']     ?? ''));
$missions= $body['missions'] ?? [];
$xp      = intval($body['xp'] ?? 0);
$streak  = intval($body['streak'] ?? 0);
$mastery = $body['mastery'] ?? [];
$errors  = $body['errors']  ?? [];

if(!$code){ echo json_encode(['ok'=>false,'error'=>'Kein Code']); exit; }

try {
  $db = getDB();

  // Prüfen ob Code existiert
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
  $stmt->execute([
    $code,
    json_encode($missions),
    $xp,
    $streak,
    json_encode($mastery),
    json_encode($errors)
  ]);

  echo json_encode(['ok'=>true]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

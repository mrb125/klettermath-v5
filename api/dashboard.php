<?php
// Lehrer-Endpunkt: Schülerfortschritt abrufen
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

try {
  $db = getDB();
  $stmt = $db->query('
    SELECT
      p.code,
      p.class_name,
      p.missions,
      p.xp,
      p.streak,
      p.mastery,
      p.errors,
      p.last_active,
      c.active
    FROM km_progress p
    JOIN km_codes c ON c.code = p.code
    ORDER BY p.last_active DESC
  ');
  $rows = $stmt->fetchAll();

  // JSON-Felder dekodieren
  foreach($rows as &$r){
    $r['missions'] = json_decode($r['missions'] ?? '[]', true);
    $r['mastery']  = json_decode($r['mastery']  ?? '{}', true);
    $r['errors']   = json_decode($r['errors']   ?? '{}', true);
    $r['progress'] = count($r['missions']);
  }

  echo json_encode(['ok'=>true,'students'=>$rows]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

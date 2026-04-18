<?php
// Lehrer-Endpunkt: Schülerfortschritt abrufen
require_once 'config.php';
cors();
requireTeacher();

if(!rateLimit('dashboard', 120)){
  http_response_code(429);
  echo json_encode(['ok'=>false,'error'=>'Zu viele Anfragen']);
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
    $r['missions'] = json_decode($r['missions'] ?? '[]', true) ?: [];
    $r['mastery']  = json_decode($r['mastery']  ?? '{}', true) ?: new stdClass();
    $r['errors']   = json_decode($r['errors']   ?? '{}', true) ?: new stdClass();
    $r['progress'] = is_array($r['missions']) ? count($r['missions']) : 0;
    // Convenience-Alias für das Frontend
    $r['class']    = $r['class_name'];
    $r['active']   = (bool)(int)$r['active'];
  }

  echo json_encode(['ok'=>true,'students'=>$rows]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

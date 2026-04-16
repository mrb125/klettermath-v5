<?php
// Lehrer-Endpunkt: Codes verwalten
// Authentifizierung via Header: X-Teacher-Key: <key aus GitHub Secrets>
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$body   = json_decode(file_get_contents('php://input'), true) ?? [];
$db     = getDB();

// GET: alle Codes auflisten
if($method === 'GET'){
  $stmt = $db->query('SELECT code, class_name, created_at, active FROM km_codes ORDER BY created_at DESC');
  echo json_encode(['ok'=>true,'codes'=>$stmt->fetchAll()]);
  exit;
}

// POST: neuen Code erstellen
if($method === 'POST' && ($body['action'] ?? '') === 'create'){
  $class = trim($body['class'] ?? 'Unbekannt');
  $count = intval($body['count'] ?? 1);
  $count = min($count, 50); // max 50 auf einmal

  $created = [];
  for($i=0; $i<$count; $i++){
    $code = strtoupper(substr(str_shuffle('ABCDEFGHJKLMNPQRSTUVWXYZ23456789'), 0, 6));
    try {
      $db->prepare('INSERT INTO km_codes (code, class_name) VALUES (?, ?)')->execute([$code, $class]);
      $created[] = $code;
    } catch(Exception $e){ /* Code-Kollision, überspringen */ }
  }
  echo json_encode(['ok'=>true,'created'=>$created]);
  exit;
}

// POST: Code deaktivieren
if($method === 'POST' && ($body['action'] ?? '') === 'deactivate'){
  $code = strtoupper(trim($body['code'] ?? ''));
  $db->prepare('UPDATE km_codes SET active=0 WHERE code=?')->execute([$code]);
  echo json_encode(['ok'=>true]);
  exit;
}

// POST: Code löschen
if($method === 'POST' && ($body['action'] ?? '') === 'delete'){
  $code = strtoupper(trim($body['code'] ?? ''));
  $db->prepare('DELETE FROM km_codes WHERE code=?')->execute([$code]);
  echo json_encode(['ok'=>true]);
  exit;
}

http_response_code(400);
echo json_encode(['ok'=>false,'error'=>'Unbekannte Aktion']);

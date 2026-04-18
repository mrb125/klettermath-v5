<?php
// Lehrer-Endpunkt: Codes verwalten
// Authentifizierung via Header: X-Teacher-Key
require_once 'config.php';
cors();
requireTeacher();

// Schutz gegen Missbrauch (auch nach erfolgreicher Auth sinnvoll).
if(!rateLimit('codes', 120)){
  http_response_code(429);
  echo json_encode(['ok'=>false,'error'=>'Zu viele Anfragen — bitte kurz warten.']);
  exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$body   = json_decode(file_get_contents('php://input'), true) ?? [];
$db     = getDB();

// GET: alle Codes auflisten
if($method === 'GET'){
  $stmt = $db->query('SELECT code, class_name, created_at, active FROM km_codes ORDER BY created_at DESC');
  $rows = $stmt->fetchAll();
  foreach($rows as &$r){
    $r['class']  = $r['class_name'];
    $r['active'] = (bool)(int)$r['active'];
  }
  echo json_encode(['ok'=>true,'codes'=>$rows]);
  exit;
}

$action = $body['action'] ?? '';

// POST: neue Codes erstellen
if($method === 'POST' && $action === 'create'){
  $class = trim($body['class'] ?? 'Unbekannt');
  if($class === '' || mb_strlen($class) > 100){
    http_response_code(400);
    echo json_encode(['ok'=>false,'error'=>'Ungültige Klasse']); exit;
  }
  $count = intval($body['count'] ?? 1);
  $count = max(1, min($count, 50));

  $created = [];
  $attempts = 0;
  while(count($created) < $count && $attempts < $count * 4){
    $attempts++;
    $code = secureCode(6);
    try {
      $db->prepare('INSERT INTO km_codes (code, class_name) VALUES (?, ?)')->execute([$code, $class]);
      $created[] = ['code'=>$code, 'class'=>$class, 'active'=>true];
    } catch(Exception $e){ /* Kollision — neuer Versuch */ }
  }
  // Liefere sowohl "codes" (Objekt-Array, vom Frontend erwartet) als auch
  // "created" (Strings, rückwärtskompatibel) zurück.
  echo json_encode(['ok'=>true, 'codes'=>$created, 'created'=>array_column($created,'code')]);
  exit;
}

$codeArg = isset($body['code']) ? strtoupper(trim($body['code'])) : '';
$validCode = (bool)preg_match('/^[A-Z0-9]{4,20}$/', $codeArg);

// POST: Code aktivieren/deaktivieren/löschen
if($method === 'POST' && in_array($action, ['activate','deactivate','delete'], true)){
  if(!$validCode){ http_response_code(400); echo json_encode(['ok'=>false,'error'=>'Ungültiger Code']); exit; }
  if($action === 'activate'){
    $db->prepare('UPDATE km_codes SET active=1 WHERE code=?')->execute([$codeArg]);
  } elseif($action === 'deactivate'){
    $db->prepare('UPDATE km_codes SET active=0 WHERE code=?')->execute([$codeArg]);
  } else {
    $db->prepare('DELETE FROM km_codes WHERE code=?')->execute([$codeArg]);
  }
  echo json_encode(['ok'=>true]);
  exit;
}

http_response_code(400);
echo json_encode(['ok'=>false,'error'=>'Unbekannte Aktion']);

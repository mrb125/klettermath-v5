<?php
// Kontrollpark — Submission eines Schueler-Ergebnisses
// Erwartet JSON-Body: {code, k, p, pn, ts, dur, pct, f, t, hits[], missed[], fp[], sig, sig_ok}
require_once 'config.php';
cors();

$body = json_decode(file_get_contents('php://input'), true);
if(!$body){ http_response_code(400); echo json_encode(['ok'=>false,'error'=>'Kein Body']); exit; }

$studentCode = substr(trim($body['n'] ?? ''), 0, 32);
$classCode   = strtoupper(substr(trim($body['k'] ?? ''), 0, 64));
$parkId      = substr(trim($body['p'] ?? ''), 0, 64);
$parkName    = substr(trim($body['pn'] ?? ''), 0, 128);
$pct         = intval($body['pct'] ?? 0);
$hits        = is_array($body['hits'] ?? null) ? $body['hits'] : [];
$missed      = is_array($body['missed'] ?? null) ? $body['missed'] : [];
$fp          = is_array($body['fp'] ?? null) ? $body['fp'] : [];
$found       = intval($body['f'] ?? count($hits));
$total       = intval($body['t'] ?? 0);
$dur         = intval($body['dur'] ?? 0);
$sig         = substr(trim($body['sig'] ?? ''), 0, 32);
$sigOk       = isset($body['sig_ok']) ? ($body['sig_ok'] ? 1 : 0) : null;
$clientTs    = intval($body['ts'] ?? 0);

if(!$studentCode){ echo json_encode(['ok'=>false,'error'=>'Kein Schuelercode']); exit; }

try {
  $db = getDB();

  // Server-seitige Validierung: Code muss von Lehrkraft angelegt sein
  $chk = $db->prepare('SELECT class_code FROM km_kp_students WHERE student_code=?');
  $chk->execute([$studentCode]);
  $reg = $chk->fetch();
  if(!$reg){
    echo json_encode(['ok'=>false,'error'=>'Dein Code ist nicht registriert. Bitte frage deine Lehrkraft, ob der Code angelegt wurde.']);
    exit;
  }
  // Klassenkonsistenz: wenn der Schueler einen Klassencode mitschickt, muss er zum
  // registrierten Klassencode passen. Falls leer, uebernehmen wir den registrierten.
  if($classCode && $reg['class_code'] && $reg['class_code'] !== $classCode){
    echo json_encode(['ok'=>false,'error'=>'Dein Code gehoert zu einer anderen Klasse ('.$reg['class_code'].').']);
    exit;
  }
  if(!$classCode) $classCode = $reg['class_code'];

  $stmt = $db->prepare('
    INSERT INTO km_kp_submissions
      (student_code, class_code, park_id, park_name, pct, found_count, total_count,
       missed_count, fp_count, dur_sec, hits_json, missed_json, fp_json, sig, sig_ok, client_ts)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  ');
  $stmt->execute([
    $studentCode, $classCode, $parkId, $parkName, $pct,
    $found, $total, count($missed), count($fp), $dur,
    json_encode($hits, JSON_UNESCAPED_UNICODE),
    json_encode($missed, JSON_UNESCAPED_UNICODE),
    json_encode($fp, JSON_UNESCAPED_UNICODE),
    $sig, $sigOk, $clientTs
  ]);
  echo json_encode(['ok'=>true, 'id'=>$db->lastInsertId()]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

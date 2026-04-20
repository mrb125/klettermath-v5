<?php
// Kontrollpark — Lehrer-Endpunkt: alle Submissions lesen
// Optional: ?klasse=KLASSENCODE fuer Filter
// Header X-Teacher-Key muss TEACHER_KEY entsprechen
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

$klasse = strtoupper(trim($_GET['klasse'] ?? ''));
$limit  = min(1000, max(1, intval($_GET['limit'] ?? 500)));

try {
  $db = getDB();
  if($klasse){
    $stmt = $db->prepare('SELECT * FROM km_kp_submissions WHERE class_code=? ORDER BY created_at DESC LIMIT '.$limit);
    $stmt->execute([$klasse]);
  } else {
    $stmt = $db->prepare('SELECT * FROM km_kp_submissions ORDER BY created_at DESC LIMIT '.$limit);
    $stmt->execute();
  }
  $rows = $stmt->fetchAll();
  foreach($rows as &$r){
    $r['hits']   = json_decode($r['hits_json']   ?? '[]', true) ?? [];
    $r['missed'] = json_decode($r['missed_json'] ?? '[]', true) ?? [];
    $r['fp']     = json_decode($r['fp_json']     ?? '[]', true) ?? [];
    unset($r['hits_json'], $r['missed_json'], $r['fp_json']);
  }
  // Aggregat: haeufigste verpasste / falsch markierte Regeln
  $missedAgg=[]; $fpAgg=[]; $ruleStats=[
    'C1'=>['h'=>0,'m'=>0], 'D1'=>['h'=>0,'m'=>0], 'B1'=>['h'=>0,'m'=>0],
    'F1'=>['h'=>0,'m'=>0], 'E1'=>['h'=>0,'m'=>0], 'G1'=>['h'=>0,'m'=>0]
  ];
  foreach($rows as $r){
    foreach($r['missed'] as $m){
      $missedAgg[$m] = ($missedAgg[$m] ?? 0) + 1;
      if(preg_match('/(C1|D1|B1|F1|E1|G1)/', $m, $mm)) $ruleStats[$mm[1]]['m']++;
    }
    foreach($r['fp'] as $f){
      $fpAgg[$f] = ($fpAgg[$f] ?? 0) + 1;
    }
    foreach($r['hits'] as $h){
      if(preg_match('/(C1|D1|B1|F1|E1|G1)/', $h, $mm)) $ruleStats[$mm[1]]['h']++;
    }
  }
  arsort($missedAgg); arsort($fpAgg);

  echo json_encode([
    'ok'=>true,
    'count'=>count($rows),
    'submissions'=>$rows,
    'topMissed'=>array_slice($missedAgg,0,10,true),
    'topFp'=>array_slice($fpAgg,0,10,true),
    'ruleStats'=>$ruleStats
  ], JSON_UNESCAPED_UNICODE);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

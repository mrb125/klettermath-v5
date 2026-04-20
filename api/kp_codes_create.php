<?php
// Kontrollpark — Lehrer legt N Schueler-Codes fuer eine Klasse an
// POST JSON: {klasse, count, labels?[]}
// Header X-Teacher-Key muss TEACHER_KEY entsprechen
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

$body   = json_decode(file_get_contents('php://input'), true);
$klasse = strtoupper(trim($body['klasse'] ?? ''));
$count  = intval($body['count'] ?? 0);
$labels = is_array($body['labels'] ?? null) ? $body['labels'] : [];

if(!$klasse){ echo json_encode(['ok'=>false,'error'=>'klasse fehlt']); exit; }
if($count < 1 || $count > 100){ echo json_encode(['ok'=>false,'error'=>'count 1..100']); exit; }

function genCode(){
  // Alphabet ohne O/0/I/1/L — konsistent zum Frontend
  $alpha = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
  $s = 'KP-';
  for($i=0;$i<4;$i++) $s .= $alpha[random_int(0, strlen($alpha)-1)];
  return $s;
}

try {
  $db = getDB();
  $db->exec("CREATE TABLE IF NOT EXISTS km_kp_students (
    student_code   VARCHAR(32) PRIMARY KEY,
    class_code     VARCHAR(64) NOT NULL DEFAULT '',
    assigned_label VARCHAR(128) DEFAULT '',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_class (class_code)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8");

  $ins = $db->prepare('INSERT IGNORE INTO km_kp_students (student_code, class_code, assigned_label) VALUES (?,?,?)');
  $created = [];
  $attempts = 0;
  while(count($created) < $count && $attempts < $count*10){
    $attempts++;
    $code = genCode();
    $label = $labels[count($created)] ?? '';
    $ins->execute([$code, $klasse, $label]);
    if($ins->rowCount() > 0) $created[] = ['code'=>$code,'label'=>$label];
  }
  echo json_encode(['ok'=>true, 'created'=>$created, 'klasse'=>$klasse]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

<?php
// Wird von GitHub Actions generiert — NICHT committen
define('DB_HOST', 'localhost');
define('DB_NAME', 'PLACEHOLDER');
define('DB_USER', 'PLACEHOLDER');
define('DB_PASS', 'PLACEHOLDER');
define('TEACHER_KEY', 'PLACEHOLDER');
// Separater Schlüssel für setup.php (einmaliges Anlegen der Tabellen).
// Wird wie TEACHER_KEY aus GitHub Secrets eingesetzt.
if(!defined('SETUP_KEY')) define('SETUP_KEY', 'PLACEHOLDER');
// Erlaubte Origins für CORS (Komma-getrennt). '*' erlaubt alle (nicht empfohlen).
if(!defined('ALLOWED_ORIGINS')) define('ALLOWED_ORIGINS', 'https://mrbl.4lima.de');

function getDB(){
  static $pdo = null;
  if($pdo) return $pdo;
  $pdo = new PDO(
    'mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4',
    DB_USER, DB_PASS,
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
     PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
     PDO::ATTR_EMULATE_PREPARES => false]
  );
  return $pdo;
}

function cors(){
  $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
  $allowed = array_map('trim', explode(',', ALLOWED_ORIGINS));
  if(in_array('*', $allowed, true)){
    header('Access-Control-Allow-Origin: *');
  } elseif($origin && in_array($origin, $allowed, true)){
    header('Access-Control-Allow-Origin: '.$origin);
    header('Vary: Origin');
  }
  header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
  header('Access-Control-Allow-Headers: Content-Type, X-Teacher-Key, X-Setup-Key');
  header('X-Content-Type-Options: nosniff');
  header('X-Frame-Options: DENY');
  header('Referrer-Policy: no-referrer');
  if($_SERVER['REQUEST_METHOD']==='OPTIONS'){ http_response_code(204); exit; }
  header('Content-Type: application/json; charset=utf-8');
}

/* Krypto-sicherer 6-Zeichen-Code (Alphabet ohne I/O/0/1). */
function secureCode($len = 6){
  $alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  $max = strlen($alphabet) - 1;
  $out = '';
  for($i=0; $i<$len; $i++){ $out .= $alphabet[random_int(0, $max)]; }
  return $out;
}

/* Minuten-Rate-Limit pro IP+Bucket. true = erlaubt. */
function rateLimit($bucket, $maxPerMinute = 30){
  $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
  if(function_exists('apcu_enabled') && apcu_enabled()){
    $key = 'km_rl:'.$bucket.':'.$ip.':'.floor(time()/60);
    $n = apcu_inc($key, 1, $ok, 120);
    return $n !== false && $n <= $maxPerMinute;
  }
  try {
    $db = getDB();
    $db->exec("CREATE TABLE IF NOT EXISTS km_rate (
      bucket VARCHAR(60) NOT NULL,
      ip     VARCHAR(45) NOT NULL,
      ts     INT NOT NULL,
      n      INT DEFAULT 1,
      PRIMARY KEY (bucket, ip, ts)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    $ts = (int)floor(time()/60);
    $db->prepare('INSERT INTO km_rate (bucket, ip, ts, n) VALUES (?,?,?,1)
      ON DUPLICATE KEY UPDATE n = n + 1')->execute([$bucket,$ip,$ts]);
    $stmt = $db->prepare('SELECT n FROM km_rate WHERE bucket=? AND ip=? AND ts=?');
    $stmt->execute([$bucket,$ip,$ts]);
    $row = $stmt->fetch();
    if(random_int(1,20)===1) $db->exec('DELETE FROM km_rate WHERE ts < '.($ts-10));
    return !$row || (int)$row['n'] <= $maxPerMinute;
  } catch(Exception $e){ return true; }
}

/* Einheitliche Prüfung des Teacher-Keys mit Timing-Safe-Compare. */
function requireTeacher(){
  $key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
  if(!is_string($key) || !hash_equals(TEACHER_KEY, $key)){
    http_response_code(403);
    echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
    exit;
  }
}

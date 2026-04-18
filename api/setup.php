<?php
// Einmalig ausführen um Tabellen zu erstellen.
// Schutz: Setup-Schlüssel erforderlich (Header X-Setup-Key oder ?key=…).
// Alternativ per .htaccess sperren.
require_once 'config.php';
cors();

$provided = $_SERVER['HTTP_X_SETUP_KEY'] ?? ($_GET['key'] ?? '');
if(!is_string($provided) || SETUP_KEY === 'PLACEHOLDER' || !hash_equals(SETUP_KEY, $provided)){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Setup-Schlüssel fehlt oder ist falsch.']);
  exit;
}
if(!rateLimit('setup', 5)){
  http_response_code(429);
  echo json_encode(['ok'=>false,'error'=>'Zu viele Setup-Versuche']);
  exit;
}

$db = getDB();

$db->exec("
  CREATE TABLE IF NOT EXISTS km_codes (
    code       VARCHAR(20) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active     TINYINT(1) DEFAULT 1
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

  CREATE TABLE IF NOT EXISTS km_progress (
    code        VARCHAR(20) PRIMARY KEY,
    class_name  VARCHAR(100) DEFAULT '',
    missions    TEXT,
    xp          INT DEFAULT 0,
    streak      INT DEFAULT 0,
    mastery     TEXT,
    errors      TEXT,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code) REFERENCES km_codes(code) ON DELETE CASCADE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
");

echo json_encode(['ok' => true, 'msg' => 'Tabellen erstellt']);

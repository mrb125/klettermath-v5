<?php
// Einmaliges Setup der Kontrollpark-Tabelle. Mit TEACHER_KEY gated.
// Nach erfolgreichem Anlegen kann diese Datei entfernt werden.
require_once 'config.php';
cors();

$key = $_GET['key'] ?? $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Teacher-Key erforderlich: ?key=XXX']);
  exit;
}

try {
  $db = getDB();
  $db->exec("
    CREATE TABLE IF NOT EXISTS km_kp_submissions (
      id            INT AUTO_INCREMENT PRIMARY KEY,
      student_code  VARCHAR(32) NOT NULL,
      class_code    VARCHAR(64) DEFAULT '',
      park_id       VARCHAR(64) DEFAULT '',
      park_name     VARCHAR(128) DEFAULT '',
      pct           INT DEFAULT 0,
      found_count   INT DEFAULT 0,
      total_count   INT DEFAULT 0,
      missed_count  INT DEFAULT 0,
      fp_count      INT DEFAULT 0,
      dur_sec       INT DEFAULT 0,
      hits_json     TEXT DEFAULT NULL,
      missed_json   TEXT DEFAULT NULL,
      fp_json       TEXT DEFAULT NULL,
      sig           VARCHAR(32) DEFAULT '',
      sig_ok        TINYINT(1) DEFAULT NULL,
      client_ts     BIGINT DEFAULT 0,
      created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_class (class_code),
      INDEX idx_student (student_code),
      INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  ");
  // Status pruefen
  $stmt = $db->query("SELECT COUNT(*) AS n FROM km_kp_submissions");
  $row = $stmt->fetch();
  echo json_encode(['ok'=>true, 'msg'=>'Tabelle km_kp_submissions angelegt/vorhanden', 'rows'=>intval($row['n'])]);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler: '.$e->getMessage()]);
}

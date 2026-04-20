<?php
// Kontrollpark — Lehrer listet angelegte Schueler-Codes einer Klasse
// GET ?klasse=XXX  (optional: leer = alle)
// Header X-Teacher-Key muss TEACHER_KEY entsprechen
// Liefert zusätzlich den Status: hat dieser Code bereits eine Submission?
require_once 'config.php';
cors();

$key = $_SERVER['HTTP_X_TEACHER_KEY'] ?? '';
if($key !== TEACHER_KEY){
  http_response_code(403);
  echo json_encode(['ok'=>false,'error'=>'Unauthorized']);
  exit;
}

$klasse = strtoupper(trim($_GET['klasse'] ?? ''));

try {
  $db = getDB();
  $db->exec("CREATE TABLE IF NOT EXISTS km_kp_students (
    student_code   VARCHAR(32) PRIMARY KEY,
    class_code     VARCHAR(64) NOT NULL DEFAULT '',
    assigned_label VARCHAR(128) DEFAULT '',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_class (class_code)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8");

  if($klasse){
    $stmt = $db->prepare('
      SELECT s.student_code, s.class_code, s.assigned_label, s.created_at,
             (SELECT COUNT(*) FROM km_kp_submissions b WHERE b.student_code=s.student_code) AS submission_count,
             (SELECT MAX(pct) FROM km_kp_submissions b WHERE b.student_code=s.student_code) AS best_pct,
             (SELECT MAX(created_at) FROM km_kp_submissions b WHERE b.student_code=s.student_code) AS last_submission
      FROM km_kp_students s
      WHERE s.class_code=? ORDER BY s.created_at ASC');
    $stmt->execute([$klasse]);
  } else {
    $stmt = $db->query('
      SELECT s.student_code, s.class_code, s.assigned_label, s.created_at,
             (SELECT COUNT(*) FROM km_kp_submissions b WHERE b.student_code=s.student_code) AS submission_count,
             (SELECT MAX(pct) FROM km_kp_submissions b WHERE b.student_code=s.student_code) AS best_pct,
             (SELECT MAX(created_at) FROM km_kp_submissions b WHERE b.student_code=s.student_code) AS last_submission
      FROM km_kp_students s
      ORDER BY s.class_code, s.created_at ASC');
  }
  $codes = $stmt->fetchAll();
  // Verfuegbare Klassen auflisten
  $cls = $db->query('SELECT class_code, COUNT(*) AS n FROM km_kp_students GROUP BY class_code ORDER BY class_code')->fetchAll();

  echo json_encode(['ok'=>true,'codes'=>$codes,'classes'=>$cls], JSON_UNESCAPED_UNICODE);
} catch(Exception $e){
  http_response_code(500);
  echo json_encode(['ok'=>false,'error'=>'Datenbankfehler']);
}

<?php
// Einmalig ausführen um Tabellen zu erstellen
// Danach löschen oder per .htaccess sperren
require_once 'config.php';
cors();

$db = getDB();

$db->exec("
  CREATE TABLE IF NOT EXISTS km_codes (
    code       VARCHAR(20) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active     TINYINT(1) DEFAULT 1
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

  CREATE TABLE IF NOT EXISTS km_progress (
    code        VARCHAR(20) PRIMARY KEY,
    class_name  VARCHAR(100) DEFAULT '',
    missions    TEXT DEFAULT '[]',
    xp          INT DEFAULT 0,
    streak      INT DEFAULT 0,
    mastery     TEXT DEFAULT '{}',
    errors      TEXT DEFAULT '{}',
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code) REFERENCES km_codes(code) ON DELETE CASCADE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

echo json_encode(['ok' => true, 'msg' => 'Tabellen erstellt']);

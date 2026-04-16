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
");

echo json_encode(['ok' => true, 'msg' => 'Tabellen erstellt']);

<?php
// Wird von GitHub Actions generiert — NICHT committen
define('DB_HOST', 'localhost');
define('DB_NAME', 'PLACEHOLDER');
define('DB_USER', 'PLACEHOLDER');
define('DB_PASS', 'PLACEHOLDER');
define('TEACHER_KEY', 'PLACEHOLDER');

function getDB(){
  static $pdo = null;
  if($pdo) return $pdo;
  $pdo = new PDO(
    'mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8',
    DB_USER, DB_PASS,
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
     PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]
  );
  return $pdo;
}

function cors(){
  header('Access-Control-Allow-Origin: *');
  header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
  header('Access-Control-Allow-Headers: Content-Type');
  if($_SERVER['REQUEST_METHOD']==='OPTIONS'){ http_response_code(204); exit; }
  header('Content-Type: application/json; charset=utf-8');
}

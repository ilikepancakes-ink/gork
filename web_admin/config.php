<?php
// Database configuration - will be updated by Python script
define('DB_PATH', '/path/to/neruaibot-main/data/bot_messages.db');
define('ADMIN_USER', 'admin');
define('ADMIN_PASS', 'admin123');

// Session configuration
session_start();

function isLoggedIn() {
    return isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true;
}

function requireLogin() {
    if (!isLoggedIn()) {
        header('Location: login.php');
        exit;
    }
}
?>

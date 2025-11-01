<?php
session_start();

// In a real app, this would redirect to Auth0
// For now, simulate a login
$_SESSION['user_id'] = 'test_user_123';
$_SESSION['user_email'] = 'user@example.com';
$_SESSION['user_name'] = 'Test User';

// Redirect to dashboard
header('Location: /dashboard.php');
exit;
?>

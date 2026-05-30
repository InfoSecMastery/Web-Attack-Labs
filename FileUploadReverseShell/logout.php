<?php
require_once __DIR__ . '/lib/functions.php';
session_destroy();
header('Location: index.php');
exit;
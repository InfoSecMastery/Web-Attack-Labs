<?php
require_once __DIR__ . '/lib/functions.php';

require_login();

$filename = basename($_GET['file'] ?? '');
if (empty($filename)) {
    http_response_code(404);
    die('File not found.');
}

$filepath = UPLOAD_DIR . $filename;
if (!file_exists($filepath)) {
    http_response_code(404);
    die('File not found.');
}

// Serve the file
$mime = mime_content_type($filepath);
header('Content-Type: ' . $mime);
header('Content-Disposition: inline; filename="' . $filename . '"');
header('Content-Length: ' . filesize($filepath));
readfile($filepath);
exit;
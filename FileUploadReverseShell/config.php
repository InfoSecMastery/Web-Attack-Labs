<?php
// ========== Configuration ==========
session_start();

// Users database
define('USERS', serialize([
    'alice' => 'password123',
    'bob' => 'secure456',
    'charlie' => 'test789'
]));

// Allowed image extensions (whitelist)
define('ALLOWED_EXTS', serialize(['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp']));

// Blacklisted dangerous extensions
define('BLACKLISTED_EXTS', serialize([
    'php', 'phtml', 'php3', 'php4', 'php5', 'php7', 'phar',
    'asp', 'aspx', 'exe', 'sh', 'py', 'pl', 'cgi',
    'htaccess', 'shtml', 'inc', 'htpasswd'
]));

// Magic numbers for image file signatures
define('MAGIC_NUMBERS', serialize([
    'jpeg' => "\xff\xd8\xff",
    'png'  => "\x89PNG\r\n\x1a\n",
    'gif'  => "GIF",
    'webp' => "RIFF",
    'bmp'  => "BM",
]));

// Max upload size
define('MAX_UPLOAD_SIZE', 5 * 1024 * 1024); // 5MB

// Storage directory
define('UPLOAD_DIR', __DIR__ . '/uploads/');
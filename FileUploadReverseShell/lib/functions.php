<?php
require_once __DIR__ . '/../config.php';

// ========== User Functions ==========

function authenticate($username, $password) {
    $users = unserialize(USERS);
    return isset($users[$username]) && $users[$username] === $password;
}

function is_logged_in() {
    return isset($_SESSION['user_id']);
}

function require_login() {
    if (!is_logged_in()) {
        header('Location: index.php');
        exit;
    }
}

// ========== File Management ==========

function get_user_files() {
    return $_SESSION['uploaded_files'] ?? [];
}

function add_user_file($filename, $original_name, $level) {
    if (!isset($_SESSION['uploaded_files'])) {
        $_SESSION['uploaded_files'] = [];
    }
    $_SESSION['uploaded_files'][] = [
        'filename' => $filename,
        'original_name' => $original_name,
        'security_level' => $level,
        'uploaded_at' => date('Y-m-d H:i:s')
    ];
}

function remove_user_file($filename) {
    if (isset($_SESSION['uploaded_files'])) {
        foreach ($_SESSION['uploaded_files'] as $key => $file) {
            if ($file['filename'] === $filename) {
                unset($_SESSION['uploaded_files'][$key]);
                $_SESSION['uploaded_files'] = array_values($_SESSION['uploaded_files']);
                return true;
            }
        }
    }
    return false;
}

// ========== Extension & Validation ==========

function get_extension($filename) {
    $parts = explode('.', $filename);
    return count($parts) > 1 ? strtolower(end($parts)) : '';
}

function get_allowed_extensions() {
    return unserialize(ALLOWED_EXTS);
}

function get_blacklisted_extensions() {
    return unserialize(BLACKLISTED_EXTS);
}

// ========== Magic Number Detection ==========

function check_magic_bytes($filepath) {
    $handle = fopen($filepath, 'rb');
    if (!$handle) return null;
    $header = fread($handle, 20);
    fclose($handle);

    $magic = unserialize(MAGIC_NUMBERS);
    
    // Special handling for WebP (RIFF + WEBP)
    if (substr($header, 0, 4) === "RIFF" && strpos(substr($header, 0, 12), "WEBP") !== false) {
        return 'webp';
    }
    
    foreach ($magic as $fmt => $bytes) {
        $len = strlen($bytes);
        if (substr($header, 0, $len) === $bytes) {
            return $fmt;
        }
    }
    return null;
}

// ========== Security Level Validations ==========

/**
 * Validate file upload according to security level.
 * Returns an array with 'valid' => bool and 'message' => string
 */
function validate_upload($file, $level) {
    if (!isset($file) || $file['error'] !== UPLOAD_ERR_OK) {
        return ['valid' => false, 'message' => 'No file selected or upload error.'];
    }

    $original_name = basename($file['name']);
    $ext = get_extension($original_name);
    $allowed = get_allowed_extensions();
    $blacklisted = get_blacklisted_extensions();

    if (empty($ext)) {
        return ['valid' => false, 'message' => 'File must have an extension.'];
    }

    // ========== LEVEL 1: No server-side validation ==========
    // Server accepts everything if level is 1

    // ========== LEVEL 2+: Extension blacklist ==========
    if (in_array($level, ['2', '3', '4', '5'])) {
        if (in_array($ext, $blacklisted)) {
            return ['valid' => false, 'message' => "⛔ Level {$level}: Extension \".{$ext}\" is blacklisted! Upload blocked."];
        }
    }

    // ========== LEVEL 3+: MIME type check ==========
    if (in_array($level, ['3', '4', '5'])) {
        $mime = $file['type'] ?? '';
        if (strpos($mime, 'image/') !== 0) {
            return ['valid' => false, 'message' => "⛔ Level {$level}: MIME type \"{$mime}\" is not allowed. Only image files permitted."];
        }
        if (!in_array($ext, $allowed)) {
            return ['valid' => false, 'message' => "⛔ Level {$level}: Extension \".{$ext}\" is not an allowed image type."];
        }
    }

    // Save file temporarily for further checks
    $safe_name = uniqid('upload_', true) . '.' . $ext;
    $dest = UPLOAD_DIR . $safe_name;
    
    if (!move_uploaded_file($file['tmp_name'], $dest)) {
        return ['valid' => false, 'message' => 'Failed to save file.'];
    }

    // ========== LEVEL 4+: Magic number check ==========
    if (in_array($level, ['4', '5'])) {
        $detected = check_magic_bytes($dest);
        if (!$detected) {
            unlink($dest);
            return ['valid' => false, 'message' => '⛔ Level 4: Magic number check failed. File does not appear to be a valid image.'];
        }

        $ext_to_type = ['jpg' => 'jpeg', 'jpeg' => 'jpeg', 'png' => 'png', 'gif' => 'gif', 'webp' => 'webp', 'bmp' => 'bmp'];
        $expected = $ext_to_type[$ext] ?? '';
        if ($expected && $expected !== $detected) {
            unlink($dest);
            return ['valid' => false, 'message' => "⛔ Level {$level}: Magic number mismatch! File claims to be \".{$ext}\" but actually is {$detected}."];
        }
    }

    // ========== LEVEL 5: Extra secure validation ==========
    if ($level === '5') {
        // Double-check extension whitelist
        if (!in_array($ext, $allowed)) {
            unlink($dest);
            return ['valid' => false, 'message' => '⛔ Level 5: Extension is not in the whitelist (' . implode(', ', $allowed) . ').'];
        }

        // Re-verify magic numbers
        $detected = check_magic_bytes($dest);
        $ext_to_type = ['jpg' => 'jpeg', 'jpeg' => 'jpeg', 'png' => 'png', 'gif' => 'gif', 'webp' => 'webp', 'bmp' => 'bmp'];
        $expected = $ext_to_type[$ext] ?? '';
        if (!$detected || ($expected && $detected !== $expected)) {
            unlink($dest);
            return ['valid' => false, 'message' => '⛔ Level 5: Enhanced validation failed. Upload rejected.'];
        }

        // Block double extensions like shell.php.png
        $parts = explode('.', strtolower($original_name));
        for ($i = 0; $i < count($parts) - 1; $i++) {
            if (in_array($parts[$i], $blacklisted) || in_array($parts[$i], ['php', 'phtml', 'asp'])) {
                unlink($dest);
                return ['valid' => false, 'message' => "⛔ Level 5: Suspicious double extension detected (\"{$original_name}\"). Upload rejected."];
            }
        }
    }

    // File is valid — add to session
    add_user_file($safe_name, $original_name, $level);

    $labels = [
        '1' => '🔴 Level 1 (Client-side only)',
        '2' => '🟠 Level 2 (Extension blacklist)',
        '3' => '🟡 Level 3 (MIME type check)',
        '4' => '🟢 Level 4 (Magic numbers)',
        '5' => '✅ Level 5 (Fully Secure)'
    ];
    
    return ['valid' => true, 'message' => "File uploaded successfully at {$labels[$level]}!", 'filename' => $safe_name];
}

/**
 * Get a human-readable name for a security level.
 */
function level_name($level) {
    $names = [
        '1' => '🔴 Client-side JS Only — No real security',
        '2' => '🟠 Extension Blacklist — Bypassable',
        '3' => '🟡 MIME Type Check — Bypassable',
        '4' => '🟢 Magic Number Check — Bypassable',
        '5' => '✅ Fully Secure — Multiple layers of protection'
    ];
    return $names[$level] ?? 'Unknown';
}

function level_icon($level) {
    $icons = ['1' => '🔴', '2' => '🟠', '3' => '🟡', '4' => '🟢', '5' => '✅'];
    return $icons[$level] ?? '❓';
}
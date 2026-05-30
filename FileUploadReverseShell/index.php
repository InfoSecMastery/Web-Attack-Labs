<?php
require_once __DIR__ . '/lib/functions.php';

// If already logged in, redirect to gallery
if (is_logged_in()) {
    header('Location: gallery.php');
    exit;
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');
    $level = $_POST['security_level'] ?? '1';

    if (empty($username) || empty($password)) {
        $error = 'Please enter both username and password.';
    } elseif (authenticate($username, $password)) {
        $_SESSION['user_id'] = $username;
        $_SESSION['username'] = $username;
        $_SESSION['security_level'] = $level;
        $_SESSION['uploaded_files'] = [];
        header('Location: gallery.php');
        exit;
    } else {
        $error = 'Invalid username or password.';
    }
}

$page_title = 'Login';
require_once __DIR__ . '/templates/header.php';
?>

<div class="login-container">
  <div class="login-card">
    <div class="logo">📸</div>
    <h1>InfoSecMastery Gallery</h1>
    <p class="subtitle">File Upload Vulnerability Lab</p>

    <?php if ($error): ?>
    <div class="error-message show"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>

    <form method="POST" action="index.php">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" placeholder="Enter your username" autocomplete="username">
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" placeholder="Enter your password" autocomplete="current-password">
      </div>

      <!-- Security Level Selection -->
      <div class="security-options">
        <p class="security-title">🛡️ Select Security Level</p>
        <p class="security-desc">Each level adds a new security layer. Try to bypass them!</p>

        <label class="level-option level-1">
          <input type="radio" name="security_level" value="1" checked>
          <div class="level-content">
            <span class="level-badge">🔴 Level 1</span>
            <span class="level-name">Client-side JS Only</span>
            <span class="level-desc">Only JavaScript checks the file extension in the browser. Server accepts anything.</span>
          </div>
        </label>

        <label class="level-option level-2">
          <input type="radio" name="security_level" value="2">
          <div class="level-content">
            <span class="level-badge">🟠 Level 2</span>
            <span class="level-name">Extension Blacklist</span>
            <span class="level-desc">Server blocks known dangerous extensions (.php, .asp, etc.). Try alternative extensions!</span>
          </div>
        </label>

        <label class="level-option level-3">
          <input type="radio" name="security_level" value="3">
          <div class="level-content">
            <span class="level-badge">🟡 Level 3</span>
            <span class="level-name">MIME Type Check</span>
            <span class="level-desc">Server checks Content-Type header and only allows image/ types. Can you spoof it?</span>
          </div>
        </label>

        <label class="level-option level-4">
          <input type="radio" name="security_level" value="4">
          <div class="level-content">
            <span class="level-badge">🟢 Level 4</span>
            <span class="level-name">Magic Number Check</span>
            <span class="level-desc">Server reads file header bytes to verify it's a real image. Can you embed a shell?</span>
          </div>
        </label>

        <label class="level-option level-5">
          <input type="radio" name="security_level" value="5">
          <div class="level-content">
            <span class="level-badge">✅ Level 5</span>
            <span class="level-name">Fully Secure</span>
            <span class="level-desc">Extension whitelist + MIME + magic bytes + double extension check. Maximum protection.</span>
          </div>
        </label>
      </div>

      <button type="submit" class="login-btn">🔐 Sign In</button>
    </form>

    <div class="demo-credentials">
      <p>📋 Demo Credentials</p>
      <div class="cred"><span>alice</span> <span>password123</span></div>
      <div class="cred"><span>bob</span> <span>secure456</span></div>
      <div class="cred"><span>charlie</span> <span>test789</span></div>
    </div>
  </div>
</div>

<?php require_once __DIR__ . '/templates/footer.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>InfoSecMastery Photo Gallery - <?= htmlspecialchars($page_title ?? 'Login') ?></title>
  <link rel="stylesheet" href="static/styles/style.css">
</head>
<body>
<?php if (is_logged_in()): ?>
<!-- Navigation Bar -->
<nav class="navbar">
  <div class="navbar-inner">
    <div class="nav-brand">
      <span class="brand-icon">📸</span> InfoSecMastery Gallery
    </div>
    <div class="nav-links">
      <span class="user-greeting">👋 <?= htmlspecialchars($_SESSION['username']) ?></span>
      <a href="gallery.php" class="<?= basename($_SERVER['PHP_SELF']) === 'gallery.php' ? 'active' : '' ?>">🖼️ Gallery</a>
      <a href="logout.php" class="logout-btn">🚪 Logout</a>
    </div>
  </div>
  <?php if (isset($level) && $level): ?>
  <div class="security-banner level-<?= $level ?>">
    <span class="banner-icon"><?= level_icon($level) ?></span>
    <span class="banner-text"><?= level_name($level) ?></span>
  </div>
  <?php endif; ?>
</nav>
<?php endif; ?>
<div class="main-content">
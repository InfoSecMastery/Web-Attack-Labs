# InfoSecMastery Photo Gallery — File Upload Vulnerability Lab

A deliberately vulnerable **PHP** web application designed to teach students about **File Upload Vulnerabilities** and the various security mechanisms used to prevent them. Part of the [InfoSecMastery](https://github.com/InfoSecMastery) security training series.

## 🎯 Learning Objectives

- Understand how unrestricted file uploads can lead to Remote Code Execution (RCE)
- Learn to bypass common file upload security controls
- Understand proper defense-in-depth strategies for file uploads
- Practice using Burp Suite / proxy tools to intercept and modify HTTP requests

## 💻 Running the Application

### Option 1: PHP built-in server

```bash
cd FileUploadReverseShell
php -S 0.0.0.0:5001
```

### Option 2: Docker

```bash
docker build -t infosecmastery-fileupload .
docker run -d -p 5001:80 infosecmastery-fileupload
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
- **Protection:** Server reads the file's header bytes to verify it's a real image
- **Bypass:** Prepend valid magic bytes to your shell code (e.g., `GIF89a<?php system($_GET['cmd']); ?>`)
- **Lesson:** Magic numbers are stronger but can still be bypassed with polyglots

### ✅ Level 5 — Fully Secure
- **Protection:** Combined defenses: extension whitelist, MIME, magic bytes, double extension detection, randomized filenames
- **Lesson:** Defense in depth with whitelisting is the proper approach

## 🛠️ Testing Tools

- **Burp Suite** — Intercept and modify upload requests
- **cURL** — Send raw HTTP requests
- **Python requests** — Script custom upload attempts

## 🐳 Docker Details

- Built on `php:8.2-apache`
- Runs on port **80** inside container, mapped to **5001** on host
- Uploaded files persist via Docker named volume (`uploads_data`)

## 📁 Project Structure

```
FileUploadReverseShell/
├── config.php              # Configuration (users, constants, magic numbers)
├── index.php               # Login page with security level selector
├── gallery.php             # Upload form + file gallery + JS logic
├── view.php                # Serve uploaded files securely
├── logout.php              # Session destroy
├── lib/
│   └── functions.php       # All security logic (5 levels)
├── templates/
│   ├── header.php          # Navbar + security banner
│   └── footer.php          # Closing HTML tags
├── static/styles/
│   └── style.css           # Dark theme UI
├── uploads/                # Uploaded files directory
├── Dockerfile              # php:8.2-apache image
├── docker-compose.yml      # Docker Compose config
└── README.md + tutorial.md # Documentation
```

## ⚠️ Disclaimer

This application is intentionally vulnerable for **educational purposes only**. Do not deploy it on public networks.
# 🏦 InfoSecMastery Bank — IDOR Vulnerability Demo

A deliberately vulnerable Flask web application designed to demonstrate **Insecure Direct Object Reference (IDOR)** vulnerabilities and their mitigations. This project is part of the **InfoSecMastery** security education series.

## 🎯 Purpose

This application simulates an online banking portal where users can view their dashboard and profile. The core security lesson revolves around **IDOR** — a flaw that lets an attacker access other users' private data by simply guessing or tampering with a user ID parameter in the URL.

The app lets you toggle between:

- ❌ **Vulnerable mode** — classic IDOR (anyone can view anyone's profile by changing the `user_id` query parameter)
- 🛡️ **Randomized ID mode** — uses UUIDs instead of numeric IDs (harder to guess, but still no authorization check)
- 🔒 **Identity Verification mode** — checks that the requested ID matches the logged-in user's session (proper authorization)
- ✅ **Both modes combined** — full protection

## 🧪 Demo Credentials

| Username  | Password      | Full Name             | Account Type      |
|-----------|---------------|-----------------------|-------------------|
| `alice`   | `password123` | Alice Johnson         | Premium Checking  |
| `bob`     | `secure456`   | Robert "Bob" Williams | Business Account  |
| `charlie` | `test789`     | Charlotte Martinez    | Student Account   |

## 🚀 Quick Start

### Option 1: Run with Docker (Recommended)

```bash
# Build and start the container
docker compose up --build
```

Then open http://localhost:5000 in your browser.

### Option 2: Run natively with Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open http://localhost:5000 in your browser.

## 🐳 Docker Details

### Dockerfile

The project includes a `Dockerfile` that:

1. Starts from a lightweight `python:3.12-slim` image
2. Installs Flask from `requirements.txt`
3. Copies the entire application
4. Exposes port **5000**
5. Runs `python app.py` on startup

### Docker Compose

The `docker-compose.yml` configuration:

- Maps host port **5000** to container port **5000**
- Mounts the project directory as a volume so the SQLite database (`bank.db`) persists across restarts
- Sets `FLASK_ENV=development`

### .dockerignore

Ignores `__pycache__`, `.pyc`/`.pyo` files, `.git`, `.vscode`, `README.md`, and `bank.db` from the Docker build context for a leaner image.

## 🧪 How to Test the IDOR Vulnerability

1. **Log in** as any user (e.g., `alice` / `password123`).
2. Click **Profile** — you'll see your own profile.
3. **Try the IDOR attack** (in vulnerable mode):
   - Change the URL from `?user_id=5001` to `?user_id=5002`.
   - You will now see **Bob's** profile with his full personal details, financial data, and even his social security number! 🚨
4. **Enable protection**:
   - On the login page, check one or both security checkboxes before logging in.
   - Re-run the same IDOR test — observe how the attack is blocked.

## 📁 Project Structure

```
├── app.py                 # Main Flask application (routes, logic)
├── database.py             # Database initialization, queries, seed data
├── bank.db                 # SQLite database (auto-created on first run)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Files to exclude from Docker build
├── README.md               # This file
├── templates/
│   ├── base.html           # Base layout with navigation & security banner
│   ├── login.html          # Login page with security mode checkboxes
│   ├── dashboard.html      # User dashboard (balance, spending, transactions)
│   └── profile.html        # User profile (sensitive personal data)
├── static/
│   └── styles/
│       └── style.css       # Application styles
├── styles/
│   └── style.css           # Static HTML version styles
├── js/
│   ├── auth.js             # Static HTML auth logic
│   └── data.js             # Static HTML data
├── index.html              # Static HTML version - login
├── dashboard.html          # Static HTML version - dashboard
└── profile.html            # Static HTML version - profile
```

## 🔐 Security Modes Explained

### 1. Vulnerable Mode (default)

The profile page accepts a `user_id` query parameter and returns that user's data with **no authorization check**. Simply changing `?user_id=5002` in the URL lets you view another user's full profile.

```python
# Example of the vulnerable code path:
target_user_id = request.args.get('user_id', type=int)
target_user = find_user_by_id(target_user_id)
# No check that target_user_id == current user's ID!
```

### 2. Randomized ID Mode

Numeric IDs are replaced with **UUIDs** (e.g., `9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d`). While UUIDs are harder to guess, if an attacker discovers one (e.g., via a data leak or another vulnerability), there's still **no authorization check**.

```python
if security_mode in ('randomized', 'both'):
    target_user_uuid = request.args.get('user_id', type=str, default='')
    target_user = find_user_by_uuid(target_user_uuid)
    # Still no identity check — just harder to enumerate
```

### 3. Identity Verification Mode

Before displaying a profile, the app checks whether the requested `user_id` matches the logged-in user's session ID. This is a **proper authorization control**.

```python
is_own_profile = (target_user['id'] == user['id'])
if identity_mode and not is_own_profile:
    return render_template('profile.html', error='...cannot view profile of user...')
```

### 4. Both Modes Combined

Applies both UUID randomization **and** identity verification for defense in depth.

## 📝 License

This project is for **educational purposes only**. It is intentionally insecure to demonstrate security vulnerabilities. Do not deploy in production.

---

Built for [InfoSecMastery](https://github.com/your-username/InfoSecMastery) — learn, hack, and secure. 🛡️
from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, find_user_by_credentials, find_user_by_id, find_user_by_uuid, get_spending, get_transactions, regenerate_uuids
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey-for-demo-only-not-for-production'

# Initialize the database on startup
with app.app_context():
    init_db()

def get_logged_in_user():
    """Get the currently logged-in user from session."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return find_user_by_id(user_id)

# Make security_mode available in all templates
@app.context_processor
def inject_security_mode():
    return dict(security_mode=session.get('security_mode', 'vulnerable'))

# ========== ROUTES ==========

@app.route('/')
def home():
    """If logged in, redirect to dashboard. Otherwise show login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('login.html', error='Please enter both username and password.')

        user = find_user_by_credentials(username, password)

        if user:
            # Read the security mode checkboxes
            randomized_mode = request.form.get('randomized_id') == 'on'
            identity_mode = request.form.get('identity_verification') == 'on'

            # Determine the effective security mode
            if randomized_mode and identity_mode:
                security_mode = 'both'
            elif randomized_mode:
                security_mode = 'randomized'
            elif identity_mode:
                security_mode = 'identity'
            else:
                security_mode = 'vulnerable'

            # If randomized mode, regenerate UUIDs each login session
            if randomized_mode:
                uuids = regenerate_uuids()
                # Re-fetch user to get the fresh UUID
                user = find_user_by_credentials(username, password)
                session['user_uuid'] = user['uuid']
                session['profile_identifier'] = user['uuid']
            else:
                session.pop('user_uuid', None)
                session['profile_identifier'] = user['id']

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['profile_picture'] = user['profile_picture']
            session['security_mode'] = security_mode
            session['identity_mode'] = identity_mode

            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password.')

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('home'))

    spending = get_spending(user['id'])
    transactions = get_transactions(user['id'])

    # Time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = 'Good morning'
    elif hour < 18:
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'

    return render_template('dashboard.html',
                         user=user,
                         greeting=greeting,
                         spending=spending,
                         transactions=transactions,
                         security_mode=session.get('security_mode', 'vulnerable'))

@app.route('/profile')
def profile():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('home'))

    security_mode = session.get('security_mode', 'vulnerable')
    identity_mode = session.get('identity_mode', False)

    # ========== PROFILE ACCESS LOGIC ==========

    # Randomized ID mode: use UUIDs instead of numeric IDs
    if security_mode in ('randomized', 'both'):
        target_user_uuid = request.args.get('user_id', type=str, default='')

        if not target_user_uuid:
            # No UUID provided, default to own profile
            target_user_uuid = session.get('user_uuid', user['uuid'])
            target_user = find_user_by_uuid(target_user_uuid)
            if not target_user:
                target_user = user
            is_own_profile = (target_user['id'] == user['id'])
            return render_template('profile.html',
                                 user=user,
                                 target_user=target_user,
                                 is_own_profile=is_own_profile,
                                 security_mode=security_mode,
                                 error=None)

        target_user = find_user_by_uuid(target_user_uuid)
        if not target_user:
            # Invalid UUID - can't guess a valid one since they're random!
            return render_template('profile.html',
                                 user=user,
                                 target_user=user,
                                 is_own_profile=True,
                                 security_mode=security_mode,
                                 error='Invalid or unknown User ID. Randomized UUIDs prevent ID enumeration.')

        is_own_profile = (target_user['id'] == user['id'])
        return render_template('profile.html',
                             user=user,
                             target_user=target_user,
                             is_own_profile=is_own_profile,
                             security_mode=security_mode,
                             error=None)

    # Numeric ID modes (vulnerable or identity verification)
    target_user_id = request.args.get('user_id', type=int)

    if target_user_id is None:
        target_user_id = user['id']

    target_user = find_user_by_id(target_user_id)

    if not target_user:
        target_user = user
        return render_template('profile.html',
                             user=user,
                             target_user=target_user,
                             is_own_profile=True,
                             security_mode=security_mode,
                             error=f'No user exists with ID: {target_user_id}. Showing your own profile.')

    is_own_profile = (target_user['id'] == user['id'])

    # Identity verification mode: block access to other users' profiles
    if identity_mode and not is_own_profile:
        return render_template('profile.html',
                             user=user,
                             target_user=user,
                             is_own_profile=True,
                             security_mode=security_mode,
                             error=f'🔒 Identity Verification Active: You ({user["full_name"]}, ID {user["id"]}) cannot view profile of user ID {target_user_id}. The system verifies that the requested user_id matches your session.')

    return render_template('profile.html',
                         user=user,
                         target_user=target_user,
                         is_own_profile=is_own_profile,
                         security_mode=security_mode,
                         error=None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
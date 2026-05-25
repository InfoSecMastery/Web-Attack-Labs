import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bank.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_uuids():
    """Generate a UUID for each user."""
    return {
        5001: str(uuid.uuid4()),
        5002: str(uuid.uuid4()),
        5003: str(uuid.uuid4())
    }

def init_db():
    """Create tables and seed with mock users if empty."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            home_address TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            bank_id TEXT NOT NULL,
            iban TEXT NOT NULL,
            current_balance REAL NOT NULL DEFAULT 0.00,
            account_type TEXT NOT NULL,
            member_since TEXT NOT NULL,
            last_login TEXT NOT NULL,
            social_security TEXT NOT NULL,
            profile_picture TEXT NOT NULL DEFAULT '👤',
            uuid TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Completed',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS spending_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS spending_limits (
            user_id INTEGER PRIMARY KEY,
            monthly_limit REAL NOT NULL DEFAULT 10000,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')

    # Check if data already seeded
    cursor.execute('SELECT COUNT(*) as cnt FROM users')
    if cursor.fetchone()['cnt'] > 0:
        # Ensure all existing users have UUIDs
        cursor.execute('SELECT id FROM users WHERE uuid IS NULL')
        rows = cursor.fetchall()
        for row in rows:
            cursor.execute('UPDATE users SET uuid = ? WHERE id = ?', (str(uuid.uuid4()), row['id']))
        conn.commit()
        conn.close()
        return

    # Generate UUIDs
    uuids = generate_uuids()

    # Seed users
    users = [
        (5001, 'alice', 'password123', 'Alice Johnson', 'alice.johnson@email.com',
         '123 Maple Street, Apt 4B, New York, NY 10001', '+1 (212) 555-0147',
         'ISB-1001-AL', 'GB29 NWBK 6016 1331 9268 19', 24750.00,
         'Premium Checking', 'March 2019', '2026-05-20 09:15:32', '***-**-6789', '👩', uuids[5001]),
        (5002, 'bob', 'secure456', 'Robert "Bob" Williams', 'bob.williams@email.com',
         '456 Oak Avenue, Suite 2C, Los Angeles, CA 90001', '+1 (310) 555-0239',
         'ISB-1002-BW', 'GB15 MIDL 4005 1532 8845 72', 58920.35,
         'Business Account', 'July 2020', '2026-05-20 08:45:11', '***-**-2341', '👨', uuids[5002]),
        (5003, 'charlie', 'test789', 'Charlotte Martinez', 'charlie.m@email.com',
         '789 Pine Road, House 12, Chicago, IL 60601', '+1 (773) 555-0892',
         'ISB-1003-CM', 'GB42 BARC 2003 8765 4410 33', 3120.87,
         'Student Account', 'January 2024', '2026-05-19 22:30:05', '***-**-8901', '👩‍🦰', uuids[5003])
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO users (id, username, password, full_name, email, home_address,
            phone_number, bank_id, iban, current_balance, account_type, member_since,
            last_login, social_security, profile_picture, uuid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # Seed spending limits
    cursor.executemany('''
        INSERT OR REPLACE INTO spending_limits (user_id, monthly_limit)
        VALUES (?, ?)
    ''', [(5001, 10000), (5002, 50000), (5003, 2000)])

    # Seed spending categories
    categories = [
        (5001, 'Housing', 1400), (5001, 'Food', 520), (5001, 'Transport', 180),
        (5001, 'Shopping', 850), (5001, 'Entertainment', 290.50),
        (5002, 'Business Ops', 7800), (5002, 'Travel', 2400), (5002, 'Software', 1200),
        (5002, 'Office', 800), (5002, 'Meals', 250.80),
        (5003, 'Food', 340), (5003, 'Books', 210), (5003, 'Entertainment', 340.25)
    ]
    cursor.executemany('''
        INSERT OR REPLACE INTO spending_categories (user_id, category, amount)
        VALUES (?, ?, ?)
    ''', categories)

    # Seed transactions
    transactions = [
        (5001, '2026-05-18', 'Amazon Purchase', -129.99),
        (5001, '2026-05-17', 'Salary Deposit', 5000.00),
        (5001, '2026-05-15', 'Whole Foods Market', -84.37),
        (5001, '2026-05-14', 'Uber Ride', -32.50),
        (5001, '2026-05-12', 'Netflix Subscription', -15.99),
        (5002, '2026-05-19', 'Client Payment - Acme Corp', 12000.00),
        (5002, '2026-05-16', 'AWS Cloud Services', -2400.00),
        (5002, '2026-05-14', 'Office Rent', -3500.00),
        (5002, '2026-05-11', 'Starbucks', -5.75),
        (5002, '2026-05-09', 'Freelance Payment', 3500.00),
        (5003, '2026-05-17', 'Campus Bookstore', -210.00),
        (5003, '2026-05-15', 'Part-time Job Pay', 600.00),
        (5003, '2026-05-13', 'Chipotle', -14.25),
        (5003, '2026-05-10', 'Spotify Student', -5.99),
        (5003, '2026-05-08', 'Transfer from Parents', 500.00)
    ]
    cursor.executemany('''
        INSERT INTO transactions (user_id, date, description, amount)
        VALUES (?, ?, ?, ?)
    ''', transactions)

    conn.commit()
    conn.close()

def find_user_by_credentials(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def find_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def find_user_by_uuid(user_uuid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE uuid = ?', (user_uuid,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def regenerate_uuids():
    """Regenerate all user UUIDs (for fresh randomized IDs)."""
    conn = get_db()
    cursor = conn.cursor()
    uuids = generate_uuids()
    for user_id, new_uuid in uuids.items():
        cursor.execute('UPDATE users SET uuid = ? WHERE id = ?', (new_uuid, user_id))
    conn.commit()
    conn.close()
    return uuids

def get_spending(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COALESCE(SUM(amount), 0) as spent FROM transactions WHERE user_id = ? AND amount < 0', (user_id,))
    spent_row = cursor.fetchone()
    spent = abs(spent_row['spent'])

    cursor.execute('SELECT monthly_limit FROM spending_limits WHERE user_id = ?', (user_id,))
    limit_row = cursor.fetchone()
    limit = limit_row['monthly_limit'] if limit_row else 10000

    cursor.execute('SELECT COUNT(*) as cnt FROM transactions WHERE user_id = ?', (user_id,))
    txn_count = cursor.fetchone()['cnt']

    cursor.execute('SELECT category, amount FROM spending_categories WHERE user_id = ?', (user_id,))
    categories = {row['category']: row['amount'] for row in cursor.fetchall()}

    conn.close()
    return {'spent': spent, 'limit': limit, 'transactions': txn_count, 'categories': categories}

def get_transactions(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT date, description, amount, status FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 5', (user_id,))
    txns = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return txns

if __name__ == '__main__':
    init_db()
    print('Database initialized successfully.')
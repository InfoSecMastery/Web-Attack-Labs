// ========== AUTHENTICATION LOGIC ==========

// Check if user is logged in on page load
function checkAuth() {
  const currentUser = sessionStorage.getItem('currentUser');
  if (!currentUser) {
    // Not logged in - redirect to login unless already there
    const isLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');
    if (!isLoginPage) {
      window.location.href = 'index.html';
    }
    return null;
  }
  return JSON.parse(currentUser);
}

// Login function
function login(username, password) {
  const user = findUserByCredentials(username, password);
  if (user) {
    // Store logged-in user in sessionStorage (clears on tab close)
    const userSession = {
      id: user.id,
      username: user.username,
      fullName: user.fullName,
      profilePicture: user.profilePicture,
      email: user.email
    };
    sessionStorage.setItem('currentUser', JSON.stringify(userSession));
    window.location.href = 'dashboard.html';
    return true;
  }
  return false;
}

// Logout function
function logout() {
  sessionStorage.removeItem('currentUser');
  window.location.href = 'index.html';
}

// Get full user data by ID (WITHOUT authorization check - this is the IDOR vulnerability!)
function getUserProfileById(userId) {
  const currentUser = checkAuth();
  if (!currentUser) return null;
  
  // NOTE: No authorization check! Any logged-in user can view ANY user's profile
  // by simply changing the user ID in the URL. This is the IDOR vulnerability.
  return findUserById(userId);
}

// Initialize login form
function initLoginForm() {
  const form = document.getElementById('loginForm');
  const errorEl = document.getElementById('errorMessage');
  
  if (!form) return;
  
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!username || !password) {
      errorEl.textContent = 'Please enter both username and password.';
      errorEl.classList.add('show');
      return;
    }
    
    const success = login(username, password);
    
    if (!success) {
      errorEl.textContent = 'Invalid username or password. Please try again.';
      errorEl.classList.add('show');
    }
  });
  
  // Clear error on input
  document.getElementById('username').addEventListener('input', function() {
    errorEl.classList.remove('show');
  });
  document.getElementById('password').addEventListener('input', function() {
    errorEl.classList.remove('show');
  });
}

// Populate dashboard
function initDashboard() {
  const user = checkAuth();
  if (!user) return;
  
  const fullUser = findUserById(user.id);
  if (!fullUser) return;
  
  // Welcome message
  const welcomeEl = document.getElementById('welcomeMessage');
  if (welcomeEl) {
    welcomeEl.innerHTML = `Welcome back, ${fullUser.fullName.split(' ')[0]}! 👋`;
  }
  
  const subtitleEl = document.getElementById('welcomeSubtitle');
  if (subtitleEl) {
    const now = new Date();
    const hour = now.getHours();
    let timeGreeting = 'Good evening';
    if (hour < 12) timeGreeting = 'Good morning';
    else if (hour < 18) timeGreeting = 'Good afternoon';
    subtitleEl.textContent = `${timeGreeting}! Here's your financial summary for today.`;
  }
  
  // Balance
  const balanceEl = document.getElementById('currentBalance');
  if (balanceEl) {
    balanceEl.textContent = '$' + fullUser.currentBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  
  const accountTypeEl = document.getElementById('accountType');
  if (accountTypeEl) {
    accountTypeEl.textContent = fullUser.accountType + ' • ' + fullUser.bankId;
  }
  
  // Spending this month
  const spending = getSpendingThisMonth(fullUser.id);
  
  const spendingEl = document.getElementById('spendingValue');
  if (spendingEl) {
    spendingEl.textContent = '$' + spending.spent.toLocaleString('en-US', { minimumFractionDigits: 2 });
  }
  
  const spendingLimitEl = document.getElementById('spendingLimit');
  if (spendingLimitEl) {
    const used = Math.round((spending.spent / spending.limit) * 100);
    spendingLimitEl.textContent = `${used}% of $${spending.limit.toLocaleString()} limit`;
    // Update bar
    const barFill = document.getElementById('spendingBarFill');
    if (barFill) {
      barFill.style.width = Math.min(used, 100) + '%';
    }
  }
  
  // Transactions count
  const txnCountEl = document.getElementById('transactionCount');
  if (txnCountEl) {
    txnCountEl.textContent = spending.transactions + ' this month';
  }
  
  // Spending categories breakdown
  const categoriesContainer = document.getElementById('spendingCategories');
  if (categoriesContainer && spending.categories) {
    const entries = Object.entries(spending.categories);
    const maxVal = Math.max(...entries.map(([, v]) => v), 1);
    categoriesContainer.innerHTML = entries.map(([cat, val]) => `
      <div class="bar-item">
        <span class="bar-label">${cat}</span>
        <span class="bar-value">$${val.toLocaleString()}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${(val / maxVal) * 100}%;"></div>
      </div>
    `).join('');
  }
  
  // Recent transactions
  const txnList = document.getElementById('transactionList');
  if (txnList) {
    const txns = getRecentTransactions(fullUser.id);
    txnList.innerHTML = txns.map(txn => {
      const isPositive = txn.amount > 0;
      const icon = isPositive ? '📩' : '💳';
      const iconClass = isPositive ? 'deposit' : 'withdrawal';
      return `
        <div class="transaction-item">
          <div class="txn-left">
            <div class="txn-icon ${iconClass}">${icon}</div>
            <div class="txn-details">
              <div class="txn-desc">${txn.description}</div>
              <div class="txn-date">${txn.date} • ${txn.status}</div>
            </div>
          </div>
          <div class="txn-amount ${isPositive ? 'positive' : 'negative'}">
            ${isPositive ? '+' : ''}$${Math.abs(txn.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
        </div>
      `;
    }).join('');
  }
}

// Populate profile page
function initProfile() {
  const user = checkAuth();
  if (!user) return;
  
  // Get user ID from URL query parameter (THIS IS THE IDOR VULNERABILITY!)
  const urlParams = new URLSearchParams(window.location.search);
  const profileUserId = urlParams.get('user_id');
  
  // If no user_id param, show own profile
  let targetUserId = profileUserId ? parseInt(profileUserId) : user.id;
  // Also fallback to own if invalid
  if (isNaN(targetUserId)) targetUserId = user.id;
  
  const targetUser = findUserById(targetUserId);
  if (!targetUser) {
    // User not found - show error and load own profile
    const errorContainer = document.getElementById('profileError');
    if (errorContainer) {
      errorContainer.innerHTML = `
        <div class="idor-notice" style="border-color: rgba(255,77,77,0.3); background: rgba(255,77,77,0.1);">
          <div class="notice-icon">⚠️</div>
          <div class="notice-content">
            <h3 style="color:#ff6b6b;">User Not Found</h3>
            <p>No user exists with ID: ${targetUserId}. Showing your own profile instead.</p>
          </div>
        </div>
      `;
    }
    loadProfileData(user.id);
    return;
  }
  
  // Show IDOR notice if viewing someone else's profile
  const idorNotice = document.getElementById('idorNotice');
  if (idorNotice) {
    const isOwnProfile = targetUser.id === user.id;
    if (!isOwnProfile) {
      idorNotice.innerHTML = `
        <div class="idor-notice">
          <div class="notice-icon">🔓</div>
          <div class="notice-content">
            <h3>IDOR Vulnerability Exploited!</h3>
            <p>You are viewing <strong>${targetUser.fullName}'s</strong> profile, not your own! 
            The application failed to verify that you (${user.username}) are authorized to view 
            user ID ${targetUser.id}. Simply changing <code>?user_id=</code> in the URL lets you 
            access any user's sensitive information. This is an <strong>Insecure Direct Object 
            Reference (IDOR)</strong> vulnerability.</p>
          </div>
        </div>
      `;
    } else {
      idorNotice.innerHTML = `
        <div class="idor-notice">
          <div class="notice-icon">ℹ️</div>
          <div class="notice-content">
            <h3>About This Page</h3>
            <p>This page displays your personal profile information. Notice the URL parameter 
            <code>?user_id=${targetUser.id}</code>. Try changing the ID to view other users' 
            data (e.g., <code>?user_id=1</code>, <code>?user_id=2</code>).</p>
          </div>
        </div>
      `;
    }
  }
  
  loadProfileData(targetUser.id);
}

function loadProfileData(userId) {
  const targetUser = findUserById(userId);
  if (!targetUser) return;
  
  const user = checkAuth();
  if (!user) return;
  
  // Profile header
  const avatarEl = document.getElementById('profileAvatar');
  if (avatarEl) avatarEl.textContent = targetUser.profilePicture;
  
  const nameEl = document.getElementById('profileName');
  if (nameEl) nameEl.textContent = targetUser.fullName;
  
  const usernameEl = document.getElementById('profileUsername');
  if (usernameEl) usernameEl.textContent = '@' + targetUser.username;
  
  // Profile fields
  const setField = (id, value, sensitive = false) => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = value || 'N/A';
      if (sensitive) el.classList.add('sensitive');
    }
  };
  
  setField('fieldEmail', targetUser.email);
  setField('fieldPhone', targetUser.phoneNumber);
  setField('fieldAddress', targetUser.homeAddress);
  setField('fieldBankId', targetUser.bankId);
  setField('fieldIban', targetUser.iban);
  setField('fieldBalance', '$' + targetUser.currentBalance.toLocaleString('en-US', { minimumFractionDigits: 2 }), true);
  setField('fieldAccountType', targetUser.accountType);
  setField('fieldMemberSince', targetUser.memberSince);
  setField('fieldLastLogin', targetUser.lastLogin);
  setField('fieldSSN', targetUser.socialSecurity, true);
  
  // IDOR exploit box - show the "other profile" input
  const exploitBox = document.getElementById('idorExploitBox');
  if (exploitBox) {
    exploitBox.innerHTML = `
      <div class="profile-idor-exploit">
        <div class="exploit-icon">🔑</div>
        <div class="exploit-content">
          <h3>🔍 IDOR Exploit Playground</h3>
          <p>Enter any User ID (1-3) to view that user's full profile without authorization:</p>
          <div>
            <input type="number" id="idorUserIdInput" min="1" max="3" value="1" placeholder="User ID">
            <button class="go-btn" onclick="exploitIDOR()">View Profile ▸</button>
          </div>
          <p style="margin-top:8px; font-size:12px; color:#606080;">
            Try IDs: 1 (Alice), 2 (Bob), 3 (Charlotte)
          </p>
        </div>
      </div>
    `;
  }
}

// IDOR exploit function - navigates to any user's profile
function exploitIDOR() {
  const input = document.getElementById('idorUserIdInput');
  if (!input) return;
  const id = parseInt(input.value);
  if (id >= 1 && id <= 3) {
    window.location.href = 'profile.html?user_id=' + id;
  }
}

// Initialize all navbars
function initNavbar() {
  const user = checkAuth();
  if (!user) return;
  
  const navBrand = document.getElementById('navBrand');
  if (navBrand) {
    navBrand.innerHTML = `<span class="brand-icon">🏦</span> InfoSecMastery Bank`;
  }
  
  const navLinks = document.getElementById('navLinks');
  if (!navLinks) return;
  
  const currentPage = window.location.pathname.split('/').pop();
  
  navLinks.innerHTML = `
    <a href="dashboard.html" class="${currentPage === 'dashboard.html' ? 'active' : ''}">
      📊 Dashboard
    </a>
    <a href="profile.html" class="${currentPage === 'profile.html' ? 'active' : ''}">
      👤 Profile
    </a>
    <a href="#" id="navLogoutBtn" class="logout-btn">
      🚪 Logout
    </a>
  `;
  
  document.getElementById('navLogoutBtn').addEventListener('click', function(e) {
    e.preventDefault();
    logout();
  });
}
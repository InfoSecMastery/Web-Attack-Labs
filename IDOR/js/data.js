const users = [
  {
    id: 5000,
    username: "alice",
    password: "password123",
    fullName: "Alice Johnson",
    email: "alice.johnson@email.com",
    homeAddress: "123 Maple Street, Apt 4B, New York, NY 10001",
    phoneNumber: "+1 (212) 555-0147",
    bankId: "ISB-1001-AL",
    iban: "GB29 NWBK 6016 1331 9268 19",
    currentBalance: 24750.00,
    accountType: "Premium Checking",
    memberSince: "March 2019",
    lastLogin: "2026-05-20 09:15:32",
    socialSecurity: "***-**-6789",
    profilePicture: "👩"
  },
  {
    id: 5001,
    username: "bob",
    password: "secure456",
    fullName: "Robert \"Bob\" Williams",
    email: "bob.williams@email.com",
    homeAddress: "456 Oak Avenue, Suite 2C, Los Angeles, CA 90001",
    phoneNumber: "+1 (310) 555-0239",
    bankId: "ISB-1002-BW",
    iban: "GB15 MIDL 4005 1532 8845 72",
    currentBalance: 58920.35,
    accountType: "Business Account",
    memberSince: "July 2020",
    lastLogin: "2026-05-20 08:45:11",
    socialSecurity: "***-**-2341",
    profilePicture: "👨"
  },
  {
    id: 5002,
    username: "charlie",
    password: "test789",
    fullName: "Charlotte Martinez",
    email: "charlie.m@email.com",
    homeAddress: "789 Pine Road, House 12, Chicago, IL 60601",
    phoneNumber: "+1 (773) 555-0892",
    bankId: "ISB-1003-CM",
    iban: "GB42 BARC 2003 8765 4410 33",
    currentBalance: 3120.87,
    accountType: "Student Account",
    memberSince: "January 2024",
    lastLogin: "2026-05-19 22:30:05",
    socialSecurity: "***-**-8901",
    profilePicture: "👩‍🦰"
  }
];

function findUserByCredentials(username, password) {
  return users.find(u => u.username === username && u.password === password) || null;
}

function findUserById(id) {
  const numId = parseInt(id);
  return users.find(u => u.id === numId) || null;
}

function getSpendingThisMonth(userId) {
  const spendingData = {
    1: { spent: 3240.50, limit: 10000, transactions: 23, categories: { "Housing": 1400, "Food": 520, "Transport": 180, "Shopping": 850, "Entertainment": 290.50 } },
    2: { spent: 12450.80, limit: 50000, transactions: 47, categories: { "Business Ops": 7800, "Travel": 2400, "Software": 1200, "Office": 800, "Meals": 250.80 } },
    3: { spent: 890.25, limit: 2000, transactions: 12, categories: { "Tuition": 0, "Food": 340, "Rent": 0, "Books": 210, "Entertainment": 340.25 } }
  };
  return spendingData[userId] || { spent: 0, limit: 0, transactions: 0, categories: {} };
}

function getRecentTransactions(userId) {
  const transactions = {
    1: [
      { date: "2026-05-18", description: "Amazon Purchase", amount: -129.99, status: "Completed" },
      { date: "2026-05-17", description: "Salary Deposit", amount: 5000.00, status: "Completed" },
      { date: "2026-05-15", description: "Whole Foods Market", amount: -84.37, status: "Completed" },
      { date: "2026-05-14", description: "Uber Ride", amount: -32.50, status: "Completed" },
      { date: "2026-05-12", description: "Netflix Subscription", amount: -15.99, status: "Completed" }
    ],
    2: [
      { date: "2026-05-19", description: "Client Payment - Acme Corp", amount: 12000.00, status: "Completed" },
      { date: "2026-05-16", description: "AWS Cloud Services", amount: -2400.00, status: "Completed" },
      { date: "2026-05-14", description: "Office Rent", amount: -3500.00, status: "Completed" },
      { date: "2026-05-11", description: "Starbucks", amount: -5.75, status: "Completed" },
      { date: "2026-05-09", description: "Freelance Payment", amount: 3500.00, status: "Completed" }
    ],
    3: [
      { date: "2026-05-17", description: "Campus Bookstore", amount: -210.00, status: "Completed" },
      { date: "2026-05-15", description: "Part-time Job Pay", amount: 600.00, status: "Completed" },
      { date: "2026-05-13", description: "Chipotle", amount: -14.25, status: "Completed" },
      { date: "2026-05-10", description: "Spotify Student", amount: -5.99, status: "Completed" },
      { date: "2026-05-08", description: "Transfer from Parents", amount: 500.00, status: "Completed" }
    ]
  };
  return transactions[userId] || [];
}
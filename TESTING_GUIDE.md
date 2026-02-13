# Testing Guide - Self-Healing Database System
## How to Test with Real Issues

---

## 🎯 Overview

You now have **3 scripts** to test the self-healing system:

1. **create_test_issues.py** - Creates intentional database errors
2. **verify_issues.py** - Checks what issues exist
3. **realtime_self_healing_mongodb.py** - Fixes the issues

---

## 📝 Step-by-Step Testing Process

### Step 1: Create Test Issues

```bash
python issue.py
```

**What it does:**	
- Clears existing test data
- Creates 5 types of intentional errors:
  - ✅ Duplicate users (john@example.com appears 3 times!)
  - ✅ Orphaned orders (3 orders with non-existent users)
  - ✅ Missing fields (4 users without required fields)
  - ✅ Invalid data (4 orders with wrong status values)
  - ✅ 1000 products without indexes (causes slow queries)

**Output you'll see:**
```
======================================================================
Database Issue Generator
Creates test data with intentional errors for testing
======================================================================

✅ Connected to MongoDB: myapp

Generating test data with issues...
======================================================================

🗑️  Clearing existing test data...
   Cleared users, orders, and products collections

1️⃣  Creating DUPLICATE USERS...
   ✅ Created 6 users
   ⚠️  Duplicates: john@example.com (3 times), alice@example.com (2 times)

2️⃣  Creating ORPHANED ORDERS...
   ✅ Created 5 orders
   ⚠️  Orphaned orders: 3 (users don't exist)
      - nonexistent@example.com
      - deleted_user@example.com
      - ghost@example.com

3️⃣  Creating USERS WITH MISSING FIELDS...
   ✅ Created 4 incomplete users
   ⚠️  Missing fields:
      - 1 user without email
      - 1 user with empty email
      - 1 user with null email
      - 1 user without name

4️⃣  Creating ORDERS WITH INVALID DATA...
   ✅ Created 4 orders with invalid data
   ⚠️  Invalid statuses:
      - 'xyz'
      - 'unknown'
      - 'in_progress'
      - 'done'

5️⃣  Creating DATA FOR SLOW QUERIES...
   ✅ Created 1000 products
   ⚠️  No indexes created (will cause slow queries)

======================================================================
✅ Test Issues Created Successfully!
======================================================================

📊 SUMMARY OF ISSUES CREATED:

Total Documents Created:
  • Users: 10
  • Orders: 9
  • Products: 1000

Issues Created:
  1. Duplicate Records:
     ⚠️  john@example.com appears 3 times
     ⚠️  alice@example.com appears 2 times

  2. Orphaned Documents:
     ⚠️  3 orders reference non-existent users

  3. Missing Required Fields:
     ⚠️  4 users with missing/empty/null emails or names

  4. Invalid Data:
     ⚠️  4 orders with invalid status values

  5. Slow Query Potential:
     ⚠️  1000 products without indexes

======================================================================

🚀 NOW RUN THE SELF-HEALING SYSTEM:
   python realtime_self_healing_mongodb.py

📊 THEN OPEN THE DASHBOARD:
   http://localhost:5000

👀 WATCH IT DETECT AND FIX THESE ISSUES IN REAL-TIME!
======================================================================
```

---

### Step 2: Verify Issues Exist

```bash
python verify_issues.py
```

**What it does:**
- Scans your database
- Shows exactly what issues exist
- Counts how many of each type
- Shows details of each issue

**Output you'll see:**
```
======================================================================
Database Issue Verification Tool
Shows what issues exist in your database
======================================================================

✅ Connected to MongoDB: myapp

Scanning database for issues...
======================================================================

1️⃣  DUPLICATE RECORDS
----------------------------------------------------------------------
   ⚠️  Email: john@example.com
      Appears: 3 times
      IDs: ['507f1f77bcf86cd799439011', '507f1f77bcf86cd799439012', ...]

   ⚠️  Email: alice@example.com
      Appears: 2 times
      IDs: ['507f1f77bcf86cd799439013', '507f1f77bcf86cd799439014']

2️⃣  ORPHANED DOCUMENTS
----------------------------------------------------------------------
   ⚠️  Order: ORD-002
      User email: nonexistent@example.com (doesn't exist)

   ⚠️  Order: ORD-003
      User email: deleted_user@example.com (doesn't exist)

   ⚠️  Order: ORD-005
      User email: ghost@example.com (doesn't exist)

3️⃣  MISSING REQUIRED FIELDS
----------------------------------------------------------------------
   ⚠️  User ID: 507f1f77bcf86cd799439015
      Missing: email field
      Name: Charlie Brown

   ⚠️  User ID: 507f1f77bcf86cd799439016
      Missing: email field
      Name: Diana Prince

4️⃣  INVALID DATA VALUES
----------------------------------------------------------------------
   ⚠️  Order: ORD-101
      Invalid status: 'xyz'
      Valid values: pending, processing, completed, cancelled

   ⚠️  Order: ORD-102
      Invalid status: 'unknown'
      Valid values: pending, processing, completed, cancelled

5️⃣  MISSING INDEXES
----------------------------------------------------------------------
   ⚠️  Collection: products
      Missing index on: category
      Document count: 1000
      Recommendation: db.products.createIndex({category: 1})

======================================================================
📊 TOTAL ISSUES FOUND: 15
======================================================================

🔧 These issues will be detected by the self-healing system!

To see them being fixed in real-time:
  1. Run: python realtime_self_healing_mongodb.py
  2. Open: http://localhost:5000
  3. Watch the dashboard as it detects and fixes!
```

---

### Step 3: Run Self-Healing System

```bash
python realtime_self_healing_mongodb.py
```

**What happens:**
1. System starts
2. Connects to MongoDB
3. Dashboard starts on http://localhost:5000
4. Detector thread starts scanning (every 30 seconds)
5. Fixer thread waits for errors to fix

**Console output:**
```
======================================================================
 Real-Time Self-Healing MongoDB Database System
 Optimized for Intel Pentium Processors
======================================================================

CONFIGURATION:
----------------------------------------------------------------------
MONGODB_URI........................... mongodb://localhost:27017
DATABASE_NAME......................... myapp
AUTO_FIX_ENABLED...................... False
DRY_RUN............................... True
----------------------------------------------------------------------

Testing MongoDB connection...
✅ Successfully connected to MongoDB!

🌐 Starting dashboard on http://0.0.0.0:5000
   Open your browser to view real-time error detection and fixing

======================================================================
Real-Time Self-Healing System Starting
======================================================================
MongoDB URI: mongodb://localhost:27017
Database: myapp
Auto-Fix: False
Dry Run: True
Detection Interval: 30s
======================================================================

✅ Detector and Fixer threads started
Press Ctrl+C to stop

======================================================================
Detection Cycle #1
======================================================================
======================================================================
Running Health Checks
======================================================================
✅ MongoDB connection successful
✅ Database 'myapp': 3 collections, 0.15 MB data, 0.01 MB indexes
======================================================================
Analyzing Performance
======================================================================
🔍 Checking for duplicates...
⚠️  Found duplicate: john@example.com (3 times)
⚠️  Found duplicate: alice@example.com (2 times)

🔍 Checking for orphaned documents...
⚠️  Found orphaned order: ORD-002
⚠️  Found orphaned order: ORD-003
⚠️  Found orphaned order: ORD-005

🔍 Checking for missing required fields...
⚠️  Found user without email: 507f1f77bcf86cd799439015
⚠️  Found user without email: 507f1f77bcf86cd799439016

🔍 Checking data consistency...
⚠️  Found invalid status: xyz
⚠️  Found invalid status: unknown

✅ Detection cycle complete. Errors in queue: 15
```

---

### Step 4: Open Dashboard

Open your browser to: **http://localhost:5000**

**What you'll see:**

```
┌─────────────────────────────────────────────────────────────┐
│      Real-Time Self-Healing MongoDB                          │
│      ⚡ Optimized for Intel Pentium                         │
└─────────────────────────────────────────────────────────────┘

Status Cards:
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ DB Status    │ Detected     │ Fixed        │ In Queue     │
│ ● Connected  │     15       │     0        │     15       │
└──────────────┴──────────────┴──────────────┴──────────────┘

Errors Detected (Real-Time):
┌─────────────────────────────────────────────────────────────┐
│ 🚨 Errors Detected                                           │
│                                                              │
│ ⚠️  duplicate_record                      [HIGH]            │
│     Email 'john@example.com' found 3 times                  │
│     Detected at 10:30:15                                    │
│                                                              │
│ ⚠️  orphaned_document                     [HIGH]            │
│     Order ORD-002 references non-existent user              │
│     Detected at 10:30:16                                    │
│                                                              │
│ ⚠️  missing_field                         [HIGH]            │
│     User missing required field 'email'                     │
│     Detected at 10:30:17                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Scenarios

### Scenario 1: Watch Detection in Real-Time

**Steps:**
1. Create issues: `python create_test_issues.py`
2. Start healing system: `python realtime_self_healing_mongodb.py`
3. Open dashboard: http://localhost:5000
4. Wait 30 seconds
5. **Watch errors appear** in the "Errors Detected" panel

**What to observe:**
- Error counter increases
- Errors appear in the list
- Each error shows severity (red/yellow/blue)
- Timestamps show when detected

---

### Scenario 2: Enable Auto-Fixing

**Steps:**
1. Stop the system (Ctrl+C)
2. Edit `realtime_self_healing_mongodb.py`:
   ```python
   'AUTO_FIX_ENABLED': True,  # Change to True
   'DRY_RUN': True,           # Keep True (simulates)
   ```
3. Restart: `python realtime_self_healing_mongodb.py`
4. Watch dashboard

**What to observe:**
- Fixer status changes from "Idle" to "Fixing"
- "Currently Fixing" section appears
- Progress bar animates
- Errors move from "Detected" to "Fixed"
- Fixed counter increases

---

### Scenario 3: Real Fixing (Advanced)

**⚠️  WARNING: This actually changes your database!**

**Steps:**
1. Stop the system
2. Edit config:
   ```python
   'AUTO_FIX_ENABLED': True,
   'DRY_RUN': False,          # Actually fix!
   'BACKUP_BEFORE_FIX': True, # Safety!
   ```
3. Restart system
4. Watch dashboard
5. Verify in MongoDB:
   ```bash
   mongosh
   use myapp
   db.users.find({email: 'john@example.com'})  // Should show only 1
   ```

**What happens:**
- Duplicates actually deleted
- Orphaned docs moved to archive collections
- Invalid data corrected
- Indexes created

---

## 📊 Verification After Fixing

### Check if issues are fixed:

```bash
python verify_issues.py
```

**If fixes worked, you'll see:**
```
======================================================================
📊 TOTAL ISSUES FOUND: 0
======================================================================

✅ No issues found! Your database is clean.
```

---

## 🔄 Testing Cycle

**Complete Testing Loop:**

```bash
# 1. Create issues
python create_test_issues.py

# 2. Verify they exist
python verify_issues.py

# 3. Run self-healing (DRY_RUN mode first)
python realtime_self_healing_mongodb.py

# 4. Open dashboard
# http://localhost:5000

# 5. Watch it detect issues

# 6. Enable fixing (edit config, restart)

# 7. Watch it fix issues

# 8. Verify fixes worked
python verify_issues.py

# 9. Repeat!
```

---

## 💡 Testing Tips

### 1. Start Safe
Always test with:
```python
'AUTO_FIX_ENABLED': False,
'DRY_RUN': True,
```

### 2. Create Custom Issues
Edit `create_test_issues.py` to add your own test cases:
```python
def create_custom_issue(self):
    # Your custom test data
    self.db.my_collection.insert_one({
        'field': 'invalid_value'
    })
```

### 3. Monitor Logs
Watch logs in real-time:
```bash
tail -f logs/realtime_healing.log
```

### 4. Test One Issue Type at a Time
Edit `create_test_issues.py` to create only one type:
```python
def generate_all_issues(self):
    self.clear_test_data()
    self.create_duplicate_users()  # Only this one
    # Comment out others
```

### 5. Use MongoDB Compass
Install MongoDB Compass to visually see:
- Before: Duplicates, orphaned docs, etc.
- After: Clean, fixed data

---

## 🎯 What to Look For

### On Dashboard:
- ✅ Errors detected counter increases
- ✅ Errors appear in real-time
- ✅ Fixer status shows "Fixing" when working
- ✅ Progress bars animate
- ✅ Fixed counter increases
- ✅ Activity log shows events

### In Logs:
- ✅ Detection cycle messages
- ✅ "Found duplicate..." messages
- ✅ "Fixing..." messages
- ✅ "Fixed successfully" messages

### In MongoDB:
- ✅ Duplicates removed
- ✅ `collection_orphaned` created
- ✅ Invalid data corrected
- ✅ Indexes created

---

## 🐛 Troubleshooting Tests

### Issues Not Detected
**Problem:** Dashboard shows 0 errors

**Solutions:**
1. Check if test data was created:
   ```bash
   mongosh
   use myapp
   db.users.countDocuments()  // Should be > 0
   ```

2. Wait 30 seconds for detection cycle

3. Check logs for errors

### Fixes Not Applied
**Problem:** Errors detected but not fixed

**Check:**
```python
'AUTO_FIX_ENABLED': True,  # Must be True
'DRY_RUN': False,          # Must be False
```

### Dashboard Not Updating
**Problem:** Dashboard stuck

**Solutions:**
1. Refresh browser (F5)
2. Check console for JavaScript errors
3. Check system is still running
4. Check Flask didn't crash (see terminal)

---

## 📞 Quick Commands

```bash
# Create test issues
python create_test_issues.py

# Check what issues exist
python verify_issues.py

# Run self-healing system
python realtime_self_healing_mongodb.py

# View logs
tail -f logs/realtime_healing.log

# Check MongoDB
mongosh
use myapp
db.users.find()
db.orders.find()
```

---

## 🎉 Success Checklist

After testing, you should have seen:

- ✅ Issues created in database
- ✅ Issues detected by system
- ✅ Dashboard showing errors in real-time
- ✅ Fixer processing errors one by one
- ✅ Progress bars animating
- ✅ Errors moved to "Fixed" panel
- ✅ Database cleaned up
- ✅ Logs showing all activities

**Congratulations! Your self-healing database is working!** 🚀

# 🔧 Real-Time Self-Healing MongoDB Database System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4-green.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Required-2496ED.svg)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> A production-ready system that **detects database errors in real-time**,
> **fixes them one by one automatically**, and displays everything live
> on a **beautiful web dashboard**.
>
> Uses **Docker + MongoDB 4.4** for maximum CPU compatibility
> including older processors that lack AVX instructions.

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Why Docker + MongoDB 4.4?](#-why-docker--mongodb-44)
3. [Requirements](#-requirements)
4. [Project Structure](#-project-structure)
5. [Installation](#-installation)
6. [Quick Start](#-quick-start)
7. [Usage](#-usage)
8. [What Gets Detected & Fixed](#-what-gets-detected--fixed)
9. [Configuration](#-configuration)
10. [Dashboard](#-dashboard)
11. [Docker Reference](#-docker-reference)
12. [MongoDB Shell Reference](#-mongodb-shell-reference)
13. [Troubleshooting](#-troubleshooting)
14. [Contributing](#-contributing)

---

## ✨ Features

- 🔍 **Real-Time Detection** — Scans database every 30 seconds
- 🔧 **Automatic Fixing** — Processes errors one by one, safely
- 💾 **Backup Before Fix** — Creates a real MongoDB backup before every change
- 📊 **Live Dashboard** — Beautiful animated web UI at `http://localhost:5000`
- 🐳 **Docker Ready** — Works on any CPU via Docker + MongoDB 4.4
- 🛡️ **Safe Modes** — Dry-run and observe-only modes built in
- 📝 **Full Logging** — Every action logged to `logs/realtime_healing.log`
- 📱 **Mobile Friendly** — Dashboard works on phones and tablets
- ♻️ **Restore Support** — Restore from any backup at any time

---

## 🐳 Why Docker + MongoDB 4.4?

MongoDB 5.0 and above require **AVX instructions** which are missing on many older CPUs.
Running MongoDB 5.0+ on such CPUs causes an immediate crash:

```
Illegal instruction (core dumped)
```

**This project uses MongoDB 4.4 via Docker** which works on every CPU, every machine.

```
MongoDB 5.0+  →  requires AVX  →  crashes on old CPUs
MongoDB 4.4   →  no AVX needed →  works everywhere ✅
```

---

## 📦 Requirements

### System
- OS: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- RAM: 4 GB minimum (8 GB recommended)
- Disk: 2 GB free space
- Docker: 20.10+
- Python: 3.8+

### Python Packages
```
pymongo>=4.0
flask>=3.0
```

Install with:
```bash
pip install -r requirements.txt
```

### `requirements.txt`
```
pymongo>=4.0.0
flask>=3.0.0
```

---

## 📁 Project Structure

```
realtime-self-healing-mongodb/
│
├── realtime_self_healing_mongodb.py   # Main application — run this
├── create_test_issues.py              # Creates intentional DB errors for testing
├── verify_issues.py                   # Scans and reports current DB issues
│
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── LICENSE                            # MIT License
├── README.md                          # This file
│
└── logs/                              # Auto-created on first run
    └── realtime_healing.log           # All system activity logs
```

---

## 🔧 Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/realtime-self-healing-mongodb.git
cd realtime-self-healing-mongodb
```

### Step 2 — Install Docker

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

**macOS:**
```bash
brew install --cask docker
```

**Fix Docker permissions (Linux):**
```bash
sudo usermod -aG docker $USER
# Log out and log back in, or run:
newgrp docker
```

### Step 3 — Pull and Run MongoDB 4.4

```bash
docker run -d \
  --name mongodb \
  --restart always \
  -p 27017:27017 \
  -v mongodb-data:/data/db \
  mongo:4.4
```

**Verify MongoDB is running:**
```bash
docker ps
# Should show: mongo:4.4  Up X minutes  0.0.0.0:27017->27017/tcp
```

**Test the connection:**
```bash
docker exec -it mongodb mongo --eval "db.adminCommand('ping')"
# Expected: { "ok" : 1 }
```

> ⚠️ **Note:** MongoDB 4.4 uses `mongo` shell, **not** `mongosh`.
> Always use: `docker exec -it mongodb mongo`

### Step 4 — Set Up Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv env
source env/bin/activate       # Linux/macOS
# or: env\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Quick Start

```bash
# 1. Start MongoDB
docker start mongodb

# 2. Activate environment
source env/bin/activate

# 3. Create test errors in the database
python create_test_issues.py

# 4. Verify the errors exist
python verify_issues.py

# 5. Start the self-healing system
python realtime_self_healing_mongodb.py

# 6. Open dashboard in browser
#    http://localhost:5000

# 7. After fixing — verify everything is clean
python verify_issues.py
```

---

## 📖 Usage

### `create_test_issues.py`

Creates **intentional errors** in MongoDB for testing purposes.
Run this to populate the database with test data.

```bash
python create_test_issues.py
```

**Creates:**
- Duplicate user records (same email multiple times)
- Orphaned orders (referencing non-existent users)
- Users with missing required fields (no email / no name)
- Orders with invalid status values
- 1000 products without indexes (triggers slow query detection)

**Sample output:**
```
✅ Connected to MongoDB: myapp
🗑️  Clearing existing data...
1️⃣  Creating DUPLICATE USERS...      ✅ 6 users inserted
2️⃣  Creating ORPHANED ORDERS...      ✅ 5 orders inserted
3️⃣  Creating MISSING FIELDS...       ✅ 4 incomplete users
4️⃣  Creating INVALID STATUS...       ✅ 4 bad orders
5️⃣  Creating SLOW QUERY DATA...      ✅ 1000 products

Expected issues: ~13
```

---

### `verify_issues.py`

Scans the database and reports all detected issues.
Run **before** fixing to see what exists, and **after** fixing to confirm they are gone.

```bash
python verify_issues.py
```

**Sample output — before fixing:**
```
1️⃣  DUPLICATE RECORDS
   ⚠️  john@example.com  — appears 3 times

2️⃣  ORPHANED DOCUMENTS
   ⚠️  ORD-002 — references nonexistent@example.com (user missing)

3️⃣  MISSING REQUIRED FIELDS
   ⚠️  Charlie Brown — no email field

4️⃣  INVALID DATA VALUES
   ⚠️  ORD-101 — status='xyz' (valid: pending/processing/completed/cancelled)

5️⃣  MISSING INDEXES
   ⚠️  products — no index on 'category' (1000 documents)

📊 TOTAL ISSUES FOUND: 13
```

**Sample output — after fixing:**
```
1️⃣  DUPLICATE RECORDS        ✅ No duplicates found
2️⃣  ORPHANED DOCUMENTS       ✅ No orphaned documents found
3️⃣  MISSING REQUIRED FIELDS  ✅ No missing fields found
4️⃣  INVALID DATA VALUES      ✅ No invalid data found
5️⃣  MISSING INDEXES          ✅ No critical missing indexes

📊 TOTAL ISSUES FOUND: 0
✅ Your database is CLEAN!
```

---

### `realtime_self_healing_mongodb.py`

The **main application**. Starts the detector, fixer, and dashboard.

```bash
python realtime_self_healing_mongodb.py
```

**What happens:**

```
Thread 1 — DETECTOR (every 30 seconds)
  └── Scans MongoDB for all 5 error types
  └── Adds detected errors to a queue
  └── Updates the live dashboard

Thread 2 — FIXER (continuous)
  └── Takes one error from the queue
  └── Creates a real MongoDB backup first
  └── Applies the appropriate fix
  └── Marks error as resolved
  └── Takes the next error

Flask Server — DASHBOARD
  └── Serves the live dashboard at http://localhost:5000
  └── Auto-refreshes every 5 seconds
```

Press `Ctrl+C` to stop.

---

## 🔍 What Gets Detected & Fixed

| Error Type | How Detected | Fix Applied | Backup Created |
|-----------|-------------|-------------|---------------|
| **Duplicate Records** | Aggregate `$group` + `$match count > 1` | Keeps first doc, deletes extras | ✅ Yes |
| **Orphaned Documents** | Cross-reference orders vs users | Archives to `collection_orphaned` | ✅ Yes |
| **Missing Required Fields** | `$exists: false` + `null` + `""` checks | Deletes invalid document | ✅ Yes |
| **Invalid Data Values** | `$nin` check against valid values list | Sets field to default valid value | ✅ Yes |
| **Slow Queries** | MongoDB profiler, threshold 2000ms | Creates missing index | ❌ Not needed |

### Backup Strategy

Before every destructive fix, a **real MongoDB backup collection** is created:

```
users_backup_20240217_103010   ← timestamp: YYYYMMDD_HHMMSS
orders_backup_20240217_103015
```

To restore from backup:
```javascript
// Inside MongoDB shell
use myapp
db.users_backup_20240217_103010.find().forEach(doc => db.users.insertOne(doc))
```

---

## ⚙️ Configuration

Edit the `CONFIG` dictionary at the top of `realtime_self_healing_mongodb.py`:

```python
CONFIG = {
    # MongoDB
    'MONGODB_URI':    'mongodb://localhost:27017',
    'DATABASE_NAME':  'myapp',

    # Detection
    'REALTIME_CHECK_INTERVAL': 30,    # Seconds between scans
    'CHECK_DUPLICATES':        True,
    'CHECK_ORPHANED_DOCS':     True,
    'CHECK_MISSING_FIELDS':    True,
    'CHECK_DATA_CONSISTENCY':  True,
    'CHECK_SLOW_QUERIES':      True,

    # Fixing
    'AUTO_FIX_ENABLED':  True,   # Enable automatic fixing
    'DRY_RUN':           False,  # False = make real changes
    'BACKUP_BEFORE_FIX': True,   # Always backup before fixing
    'FIX_DELAY':         2,      # Seconds between fixes

    # Dashboard
    'DASHBOARD_ENABLED': True,
    'DASHBOARD_PORT':    5000,
    'DASHBOARD_HOST':    '0.0.0.0',
}
```

### Modes

| Mode | `AUTO_FIX_ENABLED` | `DRY_RUN` | Effect |
|------|--------------------|-----------|--------|
| Observe only | `False` | `True` | Detects and shows errors — no changes |
| Simulate | `True` | `True` | Processes queue, logs what would happen — no changes |
| **Live fixing** | `True` | `False` | Detects, backs up, and actually fixes ✅ |

### Performance Tuning (slower machines)

```python
'REALTIME_CHECK_INTERVAL': 120,  # Check every 2 minutes
'FIX_DELAY': 5,                  # 5 seconds between fixes
```

---

## 📊 Dashboard

Open `http://localhost:5000` in any browser after starting the system.

### Status Cards

| Card | Description |
|------|-------------|
| DB Status | Live connection indicator |
| Errors Detected | Total errors found |
| Errors Fixed | Total errors resolved |
| In Queue | Errors waiting to be fixed |
| Fixer Status | Idle / Fixing |
| Total Checks | Detection cycles completed |

### Panels

- **Currently Fixing** — Shows the active fix with animated progress bar
- **Errors Detected** — Live list, colour-coded by severity (red / yellow / blue)
- **Errors Fixed** — Green list with fix timestamps
- **Activity Log** — Last 50 system events

### Access from Other Devices

```bash
hostname -I   # Get your machine's IP address
```

Then open `http://YOUR_IP:5000` from any device on the same network.

---

## 🐳 Docker Reference

```bash
# Start container
docker start mongodb

# Stop container
docker stop mongodb

# Restart container
docker restart mongodb

# Check status
docker ps

# Check all containers (including stopped)
docker ps -a

# View logs
docker logs mongodb
docker logs -f mongodb     # Live/follow logs

# Enter MongoDB shell (use 'mongo' for version 4.4)
docker exec -it mongodb mongo

# Run single command without entering shell
docker exec -it mongodb mongo --eval "db.adminCommand('ping')"

# Resource usage
docker stats mongodb

# Remove container (data is safe in the named volume)
docker stop mongodb && docker rm mongodb
```

---

## 🍃 MongoDB Shell Reference

```bash
# Enter shell
docker exec -it mongodb mongo
```

```javascript
// Switch to database
use myapp

// List all collections (real + backups)
show collections

// Document counts
db.users.countDocuments()
db.orders.countDocuments()
db.products.countDocuments()

// Find duplicates
db.users.aggregate([
  { $group: { _id: "$email", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])

// Find orphaned orders
db.orders.find({
  user_email: { $nin: db.users.distinct("email") }
})

// Find invalid statuses
db.orders.find({
  status: { $nin: ["pending","processing","completed","cancelled"] }
})

// View backup documents
db.users_backup_20240217_103010.find().pretty()

// Restore from backup
db.users_backup_20240217_103010.find().forEach(doc => db.users.insertOne(doc))

// Drop a backup collection
db.users_backup_20240217_103010.drop()

// Exit
exit
```

---

## 🔧 Troubleshooting

### `Illegal instruction (core dumped)`
**Cause:** CPU lacks AVX instructions required by MongoDB 5.0+
**Fix:** Use MongoDB 4.4 via Docker (already handled by this project)

---

### `permission denied` — Docker socket
```bash
sudo usermod -aG docker $USER
newgrp docker       # Apply without logout
# or reboot
```

---

### `Connection refused` — MongoDB not running
```bash
docker ps -a                # Check container exists
docker start mongodb        # Start it
sleep 3                     # Wait for startup
python realtime_self_healing_mongodb.py
```

---

### Container does not exist
```bash
docker run -d --name mongodb --restart always \
  -p 27017:27017 -v mongodb-data:/data/db mongo:4.4
```

---

### `mongosh: executable file not found`
MongoDB 4.4 uses `mongo`, not `mongosh`:
```bash
# Wrong
docker exec -it mongodb mongosh

# Correct ✅
docker exec -it mongodb mongo
```

---

### Dashboard not loading
```bash
pip install flask            # Ensure Flask is installed
sudo lsof -i :5000           # Check port 5000 is free
# If busy, change port in CONFIG:
# 'DASHBOARD_PORT': 8080
```

---

### Backup not appearing
Ensure all three settings are enabled in `CONFIG`:
```python
'AUTO_FIX_ENABLED':  True,
'DRY_RUN':           False,
'BACKUP_BEFORE_FIX': True,
```

---

### High CPU / slow machine
```python
'REALTIME_CHECK_INTERVAL': 120,   # Less frequent scans
'FIX_DELAY': 5,                   # More time between fixes
```

---

### View logs
```bash
tail -f logs/realtime_healing.log
grep "ERROR"  logs/realtime_healing.log
grep "Backup" logs/realtime_healing.log
grep "Fixed"  logs/realtime_healing.log
```

---

## 🔄 Full Workflow

```
git clone → install docker → run mongo:4.4 → pip install
     │
     ▼
python create_test_issues.py    ← creates ~13 errors
     │
     ▼
python verify_issues.py         ← confirms: 13 issues found
     │
     ▼
python realtime_self_healing_mongodb.py
     │
     ├── http://localhost:5000  ← watch live dashboard
     │
     ▼
python verify_issues.py         ← confirms: 0 issues found ✅
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

**Ideas for contributions:**
- Add email/Slack notifications
- Support for PostgreSQL or MySQL
- Machine learning for error prediction
- Historical trend charts on the dashboard
- Docker Compose setup
  

## 🙏 Acknowledgements

- [MongoDB](https://www.mongodb.com/) — Database
- [Flask](https://flask.palletsprojects.com/) — Web framework
- [Docker](https://www.docker.com/) — Containerisation
- [PyMongo](https://pymongo.readthedocs.io/) — Python MongoDB driver

---

**⭐ If this project helped you, please give it a star on GitHub!**

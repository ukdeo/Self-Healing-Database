#!/usr/bin/env python3
"""
Issue Verification Script - FIXED VERSION
Checks what issues exist in the database and shows what will be detected
- Skips backup collections automatically
- No double counting of missing fields
- Shows backup contents clearly

Usage: python verify_issues.py
"""

from pymongo import MongoClient
from datetime import datetime
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'MONGODB_URI': 'mongodb://localhost:27017',
    'DATABASE_NAME': 'myapp',
}

# ============================================================================
# ISSUE VERIFIER
# ============================================================================

class IssueVerifier:
    """Verifies and displays current database issues"""

    def __init__(self):
        print("=" * 70)
        print("  Database Issue Verification Tool")
        print("  Shows what issues exist in your database")
        print("=" * 70)
        print()

        try:
            self.client = MongoClient(
                CONFIG['MONGODB_URI'],
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[CONFIG['DATABASE_NAME']]
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {CONFIG['DATABASE_NAME']}")
            print()
        except Exception as e:
            print(f"❌ Cannot connect to MongoDB: {e}")
            print()
            print("Fix: Make sure MongoDB is running:")
            print("     docker start mongodb")
            sys.exit(1)

    def is_backup_collection(self, name):
        """Returns True if collection is a backup or system collection"""
        return (
            name.startswith('system.')
            or '_backup_' in name
            or name.endswith('_orphaned')
        )

    def get_real_collections(self):
        """Returns only real collections, not backups or system ones"""
        return [
            c for c in self.db.list_collection_names()
            if not self.is_backup_collection(c)
        ]

    def get_backup_collections(self):
        """Returns only backup collections"""
        return [
            c for c in self.db.list_collection_names()
            if '_backup_' in c
        ]

    # -------------------------------------------------------------------------
    # MAIN VERIFY
    # -------------------------------------------------------------------------

    def verify_all(self):
        """Run all checks and print results"""

        print("Scanning database for issues...")
        print("=" * 70)
        print()

        total_issues = 0
        total_issues += self.check_duplicates()
        total_issues += self.check_orphaned()
        total_issues += self.check_missing_fields()
        total_issues += self.check_invalid_data()
        total_issues += self.check_indexes()

        print()
        print("=" * 70)

        if total_issues == 0:
            print("📊 TOTAL ISSUES FOUND: 0")
            print("=" * 70)
            print()
            print("✅ Your database is CLEAN! All issues have been fixed.")
        else:
            print(f"📊 TOTAL ISSUES FOUND: {total_issues}")
            print("=" * 70)
            print()
            print("🔧 These issues will be detected by the self-healing system!")
            print()
            print("To fix them:")
            print("  1. Run: python realtime_self_healing_mongodb.py")
            print("  2. Open: http://localhost:5000")
            print("  3. Watch the dashboard fix them in real-time!")

        print()

    # -------------------------------------------------------------------------
    # CHECK 1: DUPLICATES
    # -------------------------------------------------------------------------

    def check_duplicates(self):
        """Check for duplicate records"""
        print("1️⃣  DUPLICATE RECORDS")
        print("-" * 70)

        count = 0

        try:
            if 'users' not in self.get_real_collections():
                print("   ℹ️  No users collection found")
                print()
                return 0

            pipeline = [
                {'$group': {
                    '_id': '$email',
                    'count': {'$sum': 1},
                    'ids': {'$push': '$_id'}
                }},
                {'$match': {'count': {'$gt': 1}}}
            ]

            duplicates = list(self.db.users.aggregate(pipeline))

            if duplicates:
                for dup in duplicates:
                    extras = dup['count'] - 1
                    count += extras
                    print(f"   ⚠️  Email     : {dup['_id']}")
                    print(f"      Appears   : {dup['count']} times")
                    print(f"      Extra docs: {extras} (will be deleted after fix)")
                    print(f"      All IDs   : {[str(i) for i in dup['ids']]}")
                    print()
            else:
                print("   ✅ No duplicate emails found")
                print()

        except Exception as e:
            print(f"   ❌ Error checking duplicates: {e}")
            print()

        return count

    # -------------------------------------------------------------------------
    # CHECK 2: ORPHANED DOCUMENTS
    # -------------------------------------------------------------------------

    def check_orphaned(self):
        """Check for orphaned documents"""
        print("2️⃣  ORPHANED DOCUMENTS")
        print("-" * 70)

        count = 0

        try:
            real = self.get_real_collections()

            if 'users' not in real or 'orders' not in real:
                print("   ℹ️  users or orders collection not found")
                print()
                return 0

            # Get all valid emails (exclude empty/null)
            valid_emails = set(
                doc.get('email')
                for doc in self.db.users.find({}, {'email': 1})
                if doc.get('email')
            )

            orphaned = []
            for order in self.db.orders.find():
                user_email = order.get('user_email')
                if user_email and user_email not in valid_emails:
                    orphaned.append(order)

            if orphaned:
                for order in orphaned:
                    count += 1
                    print(f"   ⚠️  Order ID   : {order.get('order_id', str(order['_id']))}")
                    print(f"      User email : {order.get('user_email')} ← user does not exist")
                    print(f"      Product    : {order.get('product', 'N/A')}")
                    print(f"      Amount     : ${order.get('amount', 0)}")
                    print()
            else:
                print("   ✅ No orphaned documents found")
                print()

        except Exception as e:
            print(f"   ❌ Error checking orphaned docs: {e}")
            print()

        return count

    # -------------------------------------------------------------------------
    # CHECK 3: MISSING FIELDS  (FIXED - no double counting)
    # -------------------------------------------------------------------------

    def check_missing_fields(self):
        """Check for missing required fields"""
        print("3️⃣  MISSING REQUIRED FIELDS")
        print("-" * 70)

        count = 0

        try:
            if 'users' not in self.get_real_collections():
                print("   ℹ️  No users collection found")
                print()
                return 0

            # Track IDs already counted to avoid double counting
            already_counted = set()

            # --- Missing or empty email ---
            missing_email = list(self.db.users.find({
                '$or': [
                    {'email': {'$exists': False}},
                    {'email': None},
                    {'email': ''}
                ]
            }))

            for user in missing_email:
                uid = str(user['_id'])
                if uid not in already_counted:
                    already_counted.add(uid)
                    count += 1
                    print(f"   ⚠️  User ID : {uid}")
                    print(f"      Problem : Missing or empty 'email' field")
                    print(f"      Name    : {user.get('name', 'N/A')}")
                    print()

            # --- Missing or empty name ---
            missing_name = list(self.db.users.find({
                '$or': [
                    {'name': {'$exists': False}},
                    {'name': None},
                    {'name': ''}
                ]
            }))

            for user in missing_name:
                uid = str(user['_id'])
                # Only count if NOT already counted above
                if uid not in already_counted:
                    already_counted.add(uid)
                    count += 1
                    print(f"   ⚠️  User ID : {uid}")
                    print(f"      Problem : Missing or empty 'name' field")
                    print(f"      Email   : {user.get('email', 'N/A')}")
                    print()

            if count == 0:
                print("   ✅ No missing required fields found")
                print()

        except Exception as e:
            print(f"   ❌ Error checking missing fields: {e}")
            print()

        return count

    # -------------------------------------------------------------------------
    # CHECK 4: INVALID DATA
    # -------------------------------------------------------------------------

    def check_invalid_data(self):
        """Check for invalid data values"""
        print("4️⃣  INVALID DATA VALUES")
        print("-" * 70)

        count = 0

        try:
            if 'orders' not in self.get_real_collections():
                print("   ℹ️  No orders collection found")
                print()
                return 0

            valid_statuses = ['pending', 'processing', 'completed', 'cancelled']

            invalid_orders = list(self.db.orders.find({
                'status': {'$nin': valid_statuses}
            }))

            if invalid_orders:
                for order in invalid_orders:
                    count += 1
                    print(f"   ⚠️  Order ID      : {order.get('order_id', str(order['_id']))}")
                    print(f"      Invalid status : '{order.get('status')}'")
                    print(f"      Valid values   : {', '.join(valid_statuses)}")
                    print()
            else:
                print("   ✅ No invalid data found")
                print()

        except Exception as e:
            print(f"   ❌ Error checking invalid data: {e}")
            print()

        return count

    # -------------------------------------------------------------------------
    # CHECK 5: MISSING INDEXES
    # -------------------------------------------------------------------------

    def check_indexes(self):
        """Check for missing indexes"""
        print("5️⃣  MISSING INDEXES")
        print("-" * 70)

        count = 0

        try:
            if 'products' not in self.get_real_collections():
                print("   ℹ️  No products collection found")
                print()
                return 0

            indexes = list(self.db.products.list_indexes())
            indexed_fields = set()
            for idx in indexes:
                indexed_fields.update(idx.get('key', {}).keys())

            doc_count = self.db.products.count_documents({})

            if doc_count > 100:
                recommended = ['category', 'price', 'name']
                missing = [f for f in recommended if f not in indexed_fields]

                if missing:
                    for field in missing:
                        count += 1
                        print(f"   ⚠️  Collection : products ({doc_count} documents)")
                        print(f"      Missing    : index on '{field}'")
                        print(f"      Fix command: db.products.createIndex({{{field}: 1}})")
                        print()
                else:
                    print("   ✅ All recommended indexes exist")
                    print()
            else:
                print(f"   ℹ️  products has only {doc_count} docs (index not needed yet)")
                print()

        except Exception as e:
            print(f"   ❌ Error checking indexes: {e}")
            print()

        return count

    # -------------------------------------------------------------------------
    # DATABASE STATS
    # -------------------------------------------------------------------------

    def get_database_stats(self):
        """Print full database statistics including backups"""

        print("=" * 70)
        print("📊 DATABASE STATISTICS")
        print("=" * 70)
        print()

        try:
            stats = self.db.command('dbStats')

            print(f"  Database   : {CONFIG['DATABASE_NAME']}")
            print(f"  Collections: {stats.get('collections', 0)}")
            print(f"  Data Size  : {stats.get('dataSize', 0) / (1024 * 1024):.3f} MB")
            print(f"  Index Size : {stats.get('indexSize', 0) / (1024 * 1024):.3f} MB")
            print()

            all_collections = self.db.list_collection_names()
            real  = [c for c in all_collections if not self.is_backup_collection(c)]
            backs = [c for c in all_collections if '_backup_' in c]
            orph  = [c for c in all_collections if c.endswith('_orphaned')]

            # --- Real collections ---
            print("  📁 REAL COLLECTIONS (your actual data):")
            if real:
                for name in sorted(real):
                    cnt = self.db[name].count_documents({})
                    print(f"     • {name:<30} {cnt} documents")
            else:
                print("     (none found)")
            print()

            # --- Backup collections ---
            print("  💾 BACKUP COLLECTIONS (created before each fix):")
            if backs:
                for name in sorted(backs):
                    cnt = self.db[name].count_documents({})
                    parts = name.split('_backup_')
                    ts    = parts[1] if len(parts) > 1 else 'unknown'
                    try:
                        dt = datetime.strptime(ts, '%Y%m%d_%H%M%S')
                        ts_readable = dt.strftime('%d %b %Y at %H:%M:%S')
                    except Exception:
                        ts_readable = ts
                    print(f"     • {name:<40} {cnt} docs  [{ts_readable}]")
            else:
                print("     (no backups yet)")
                print()
                print("     ℹ️  To create backups, in realtime_self_healing_mongodb.py set:")
                print("         AUTO_FIX_ENABLED = True")
                print("         DRY_RUN          = False")
                print("         BACKUP_BEFORE_FIX = True")
            print()

            # --- Orphaned archive collections ---
            if orph:
                print("  🗂️  ORPHANED ARCHIVE COLLECTIONS (moved here by fixer):")
                for name in sorted(orph):
                    cnt = self.db[name].count_documents({})
                    print(f"     • {name:<30} {cnt} documents")
                print()

        except Exception as e:
            print(f"  ❌ Error getting stats: {e}")

        print("=" * 70)

    # -------------------------------------------------------------------------
    # BACKUP VIEWER
    # -------------------------------------------------------------------------

    def show_backup_contents(self):
        """Show detailed contents of each backup collection"""

        backs = self.get_backup_collections()

        print()
        print("=" * 70)
        print("💾 BACKUP DETAILS")
        print("=" * 70)

        if not backs:
            print()
            print("  No backups found yet.")
            print()
            print("  Backups will appear here automatically once the")
            print("  self-healing system runs with:")
            print()
            print("     AUTO_FIX_ENABLED  = True")
            print("     DRY_RUN           = False")
            print("     BACKUP_BEFORE_FIX = True")
            print()
            print("  Then run:  python realtime_self_healing_mongodb.py")
            print("=" * 70)
            return

        for name in sorted(backs):
            docs = list(self.db[name].find())
            parts = name.split('_backup_')
            original_coll = parts[0]
            ts = parts[1] if len(parts) > 1 else ''
            try:
                dt = datetime.strptime(ts, '%Y%m%d_%H%M%S')
                ts_readable = dt.strftime('%d %b %Y at %H:%M:%S')
            except Exception:
                ts_readable = ts

            print()
            print(f"  📦 Backup: {name}")
            print(f"     Original collection : {original_coll}")
            print(f"     Backed up at        : {ts_readable}")
            print(f"     Documents saved     : {len(docs)}")
            print(f"  {'─' * 60}")

            if docs:
                print(f"  Sample documents (first 3):")
                for i, doc in enumerate(docs[:3], 1):
                    clean = {k: str(v) for k, v in doc.items() if k != '_id'}
                    print(f"    [{i}] {clean}")
                if len(docs) > 3:
                    print(f"    ... and {len(docs) - 3} more documents")
            print()

        print("=" * 70)
        print()
        print("  To restore from a backup, run inside MongoDB shell:")
        print("  docker exec -it mongodb mongo")
        print("  use myapp")
        print("  db.BACKUP_NAME.find().forEach(doc => db.COLLECTION.insertOne(doc))")
        print("=" * 70)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""

    verifier = IssueVerifier()
    verifier.verify_all()
    verifier.get_database_stats()
    verifier.show_backup_contents()

    print()
    print("  Run again anytime to check current status.")
    print()

if __name__ == '__main__':
    main()

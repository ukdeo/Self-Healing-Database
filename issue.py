#!/usr/bin/env python3
"""
Database Issue Generator - IMPROVED VERSION
Creates intentional errors in MongoDB to test the self-healing system

Issues Created:
  1. Duplicate Records       - Same email appears multiple times
  2. Orphaned Documents      - Orders referencing non-existent users
  3. Missing Required Fields - Users without email or name
  4. Invalid Data Values     - Orders with wrong status values
  5. Slow Query Scenarios    - 1000 products without indexes

Usage: python create_test_issues.py
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'MONGODB_URI': 'mongodb://localhost:27017',
    'DATABASE_NAME': 'myapp',
}

# ============================================================================
# ISSUE GENERATOR
# ============================================================================

class IssueGenerator:
    """Generates test issues in the database"""

    def __init__(self):
        print()
        print("=" * 70)
        print("  Database Issue Generator")
        print("  Creates intentional errors for testing the self-healing system")
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
            print("Please make sure MongoDB is running:")
            print("   docker start mongodb")
            sys.exit(1)

    # -------------------------------------------------------------------------
    # MAIN GENERATE
    # -------------------------------------------------------------------------

    def generate_all_issues(self):
        """Generate all types of issues"""

        print("Generating test data with intentional errors...")
        print("=" * 70)
        print()

        # Step 1: Clear all old data including backups
        self.clear_all_data()

        # Step 2: Create each type of issue
        dup_count      = self.create_duplicate_users()
        orphan_count   = self.create_orphaned_orders()
        missing_count  = self.create_users_with_missing_fields()
        invalid_count  = self.create_orders_with_invalid_data()
        slow_count     = self.create_data_for_slow_queries()

        # Step 3: Print final summary
        print()
        print("=" * 70)
        print("✅ All Test Issues Created Successfully!")
        print("=" * 70)
        print()
        self.print_summary(dup_count, orphan_count, missing_count, invalid_count, slow_count)

    # -------------------------------------------------------------------------
    # CLEAR DATA
    # -------------------------------------------------------------------------

    def clear_all_data(self):
        """Clear existing test data AND old backup collections"""
        print("🗑️  Clearing existing data...")

        # Clear main collections
        r1 = self.db.users.delete_many({})
        r2 = self.db.orders.delete_many({})
        r3 = self.db.products.delete_many({})

        print(f"   Deleted {r1.deleted_count} users")
        print(f"   Deleted {r2.deleted_count} orders")
        print(f"   Deleted {r3.deleted_count} products")

        # Also drop old backup collections so they don't confuse verify_issues.py
        all_collections = self.db.list_collection_names()
        backup_colls = [c for c in all_collections if '_backup_' in c or c.endswith('_orphaned')]

        if backup_colls:
            for coll in backup_colls:
                self.db[coll].drop()
                print(f"   Dropped old backup: {coll}")
        else:
            print("   No old backups to clear")

        print()

    # -------------------------------------------------------------------------
    # ISSUE 1: DUPLICATES
    # -------------------------------------------------------------------------

    def create_duplicate_users(self):
        """Create duplicate user records"""
        print("1️⃣  Creating DUPLICATE USERS...")

        users = [
            # john@example.com appears 3 times
            {
                'email': 'john@example.com',
                'name': 'John Doe',
                'age': 28,
                'status': 'active',
                'phone': '555-0101',
                'created_at': datetime.now()
            },
            {
                'email': 'john@example.com',   # Duplicate 1
                'name': 'John Doe',
                'age': 28,
                'status': 'active',
                'phone': '555-0101',
                'created_at': datetime.now()
            },
            {
                'email': 'john@example.com',   # Duplicate 2
                'name': 'John Smith',
                'age': 30,
                'status': 'inactive',
                'phone': '555-0199',
                'created_at': datetime.now()
            },
            # alice@example.com appears 2 times
            {
                'email': 'alice@example.com',
                'name': 'Alice Johnson',
                'age': 24,
                'status': 'active',
                'phone': '555-0102',
                'created_at': datetime.now()
            },
            {
                'email': 'alice@example.com',  # Duplicate
                'name': 'Alice Johnson',
                'age': 24,
                'status': 'inactive',
                'phone': '555-0102',
                'created_at': datetime.now()
            },
            # bob@example.com - valid, no duplicate
            {
                'email': 'bob@example.com',
                'name': 'Bob Wilson',
                'age': 35,
                'status': 'active',
                'phone': '555-0103',
                'created_at': datetime.now()
            },
        ]

        result = self.db.users.insert_many(users)
        count = len(result.inserted_ids)

        print(f"   ✅ Inserted {count} users")
        print(f"   ⚠️  john@example.com  → appears 3 times (2 duplicates)")
        print(f"   ⚠️  alice@example.com → appears 2 times (1 duplicate)")
        print(f"   ✅  bob@example.com   → appears 1 time  (no duplicate)")
        print()

        return 3  # 3 extra duplicate documents

    # -------------------------------------------------------------------------
    # ISSUE 2: ORPHANED DOCUMENTS
    # -------------------------------------------------------------------------

    def create_orphaned_orders(self):
        """Create orders that reference non-existent users"""
        print("2️⃣  Creating ORPHANED ORDERS...")

        orders = [
            # Valid orders (users exist)
            {
                'order_id': 'ORD-001',
                'user_email': 'bob@example.com',       # ✅ user exists
                'product': 'Laptop',
                'amount': 999.99,
                'status': 'pending',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-004',
                'user_email': 'alice@example.com',     # ✅ user exists
                'product': 'Monitor',
                'amount': 299.99,
                'status': 'processing',
                'created_at': datetime.now()
            },
            # Orphaned orders (users do NOT exist)
            {
                'order_id': 'ORD-002',
                'user_email': 'nonexistent@example.com',   # ❌ user missing
                'product': 'Mouse',
                'amount': 29.99,
                'status': 'completed',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-003',
                'user_email': 'deleted_user@example.com',  # ❌ user missing
                'product': 'Keyboard',
                'amount': 79.99,
                'status': 'pending',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-005',
                'user_email': 'ghost@example.com',         # ❌ user missing
                'product': 'Webcam',
                'amount': 59.99,
                'status': 'cancelled',
                'created_at': datetime.now()
            },
        ]

        result = self.db.orders.insert_many(orders)
        count = len(result.inserted_ids)
        orphan_count = 3

        print(f"   ✅ Inserted {count} orders total")
        print(f"   ✅  ORD-001 → bob@example.com   (valid user)")
        print(f"   ✅  ORD-004 → alice@example.com (valid user)")
        print(f"   ⚠️  ORD-002 → nonexistent@example.com  (user missing!)")
        print(f"   ⚠️  ORD-003 → deleted_user@example.com (user missing!)")
        print(f"   ⚠️  ORD-005 → ghost@example.com         (user missing!)")
        print()

        return orphan_count

    # -------------------------------------------------------------------------
    # ISSUE 3: MISSING FIELDS
    # -------------------------------------------------------------------------

    def create_users_with_missing_fields(self):
        """Create users with missing required fields"""
        print("3️⃣  Creating USERS WITH MISSING FIELDS...")

        incomplete_users = [
            {
                # email field completely absent
                'name': 'Charlie Brown',
                'age': 22,
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': '',               # email is empty string
                'name': 'Diana Prince',
                'age': 29,
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': None,             # email is null
                'name': 'Eve Adams',
                'age': 31,
                'status': 'inactive',
                'created_at': datetime.now()
            },
            {
                'email': 'frank@example.com',
                # name field completely absent
                'age': 40,
                'status': 'active',
                'created_at': datetime.now()
            },
        ]

        result = self.db.users.insert_many(incomplete_users)
        count = len(result.inserted_ids)

        print(f"   ✅ Inserted {count} incomplete users")
        print(f"   ⚠️  Charlie Brown  → no 'email' field at all")
        print(f"   ⚠️  Diana Prince   → email is empty string ''")
        print(f"   ⚠️  Eve Adams      → email is null (None)")
        print(f"   ⚠️  frank@...      → no 'name' field at all")
        print()

        return count

    # -------------------------------------------------------------------------
    # ISSUE 4: INVALID DATA
    # -------------------------------------------------------------------------

    def create_orders_with_invalid_data(self):
        """Create orders with invalid status values"""
        print("4️⃣  Creating ORDERS WITH INVALID STATUS...")

        # Valid statuses are: pending, processing, completed, cancelled
        invalid_orders = [
            {
                'order_id': 'ORD-101',
                'user_email': 'bob@example.com',
                'product': 'Tablet',
                'amount': 399.99,
                'status': 'xyz',          # ❌ completely wrong
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-102',
                'user_email': 'alice@example.com',
                'product': 'Phone',
                'amount': 699.99,
                'status': 'unknown',      # ❌ wrong
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-103',
                'user_email': 'john@example.com',
                'product': 'Headphones',
                'amount': 149.99,
                'status': 'in_progress',  # ❌ should be 'processing'
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-104',
                'user_email': 'bob@example.com',
                'product': 'Charger',
                'amount': 19.99,
                'status': 'done',         # ❌ should be 'completed'
                'created_at': datetime.now()
            },
        ]

        result = self.db.orders.insert_many(invalid_orders)
        count = len(result.inserted_ids)

        print(f"   ✅ Inserted {count} orders with invalid status")
        print(f"   ⚠️  ORD-101 → status='xyz'         (valid: pending/processing/completed/cancelled)")
        print(f"   ⚠️  ORD-102 → status='unknown'     (valid: pending/processing/completed/cancelled)")
        print(f"   ⚠️  ORD-103 → status='in_progress' (valid: pending/processing/completed/cancelled)")
        print(f"   ⚠️  ORD-104 → status='done'        (valid: pending/processing/completed/cancelled)")
        print()

        return count

    # -------------------------------------------------------------------------
    # ISSUE 5: SLOW QUERIES
    # -------------------------------------------------------------------------

    def create_data_for_slow_queries(self):
        """Create 1000 products without indexes (causes slow queries)"""
        print("5️⃣  Creating DATA FOR SLOW QUERIES...")

        categories = ['Electronics', 'Clothing', 'Books', 'Food', 'Toys']

        products = []
        for i in range(1000):
            products.append({
                'product_id': f'PROD-{i:04d}',
                'name': f'Product {i}',
                'category': random.choice(categories),
                'price': round(random.uniform(10.0, 1000.0), 2),
                'stock': random.randint(0, 100),
                'description': (
                    f'This is product number {i}. '
                    f'A detailed description to make the document larger '
                    f'and queries slower without indexes.'
                ),
                'created_at': datetime.now() - timedelta(days=random.randint(0, 365))
            })

        # Insert in batches of 100 to be Pentium-friendly
        batch_size = 100
        total_inserted = 0
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            result = self.db.products.insert_many(batch)
            total_inserted += len(result.inserted_ids)

        print(f"   ✅ Inserted {total_inserted} products (no indexes)")
        print(f"   ⚠️  Searching by 'category' will be slow → full collection scan")
        print(f"   ⚠️  Searching by 'price'    will be slow → full collection scan")
        print(f"   ⚠️  Searching by 'name'     will be slow → full collection scan")
        print()

        return total_inserted

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------

    def print_summary(self, dup_count, orphan_count, missing_count, invalid_count, slow_count):
        """Print a clear summary of everything created"""

        total_users    = self.db.users.count_documents({})
        total_orders   = self.db.orders.count_documents({})
        total_products = self.db.products.count_documents({})

        # Count real issues for verify_issues.py
        issue_total = dup_count + orphan_count + missing_count + invalid_count + 3  # 3 indexes

        print("📊 FINAL SUMMARY")
        print("=" * 70)
        print()
        print("  Collections created:")
        print(f"     users    : {total_users}  documents")
        print(f"     orders   : {total_orders}  documents")
        print(f"     products : {total_products} documents")
        print()
        print("  Issues created (what self-healing will detect & fix):")
        print()
        print(f"     1. Duplicate Records      → {dup_count} extra docs")
        print(f"        ⚠️  john@example.com  appears 3x")
        print(f"        ⚠️  alice@example.com appears 2x")
        print()
        print(f"     2. Orphaned Orders        → {orphan_count} orphaned docs")
        print(f"        ⚠️  ORD-002 (nonexistent user)")
        print(f"        ⚠️  ORD-003 (deleted user)")
        print(f"        ⚠️  ORD-005 (ghost user)")
        print()
        print(f"     3. Missing Required Fields → {missing_count} incomplete users")
        print(f"        ⚠️  Charlie Brown  (no email field)")
        print(f"        ⚠️  Diana Prince   (empty email)")
        print(f"        ⚠️  Eve Adams      (null email)")
        print(f"        ⚠️  frank@...      (no name field)")
        print()
        print(f"     4. Invalid Data Values    → {invalid_count} bad orders")
        print(f"        ⚠️  ORD-101 status='xyz'")
        print(f"        ⚠️  ORD-102 status='unknown'")
        print(f"        ⚠️  ORD-103 status='in_progress'")
        print(f"        ⚠️  ORD-104 status='done'")
        print()
        print(f"     5. Missing Indexes        → 3 indexes missing on products")
        print(f"        ⚠️  No index on 'category'")
        print(f"        ⚠️  No index on 'price'")
        print(f"        ⚠️  No index on 'name'")
        print()
        print(f"  Expected by verify_issues.py: ~{issue_total} issues")
        print()
        print("=" * 70)
        print()
        print("  🚀 NEXT STEPS:")
        print()
        print("  Step 1 — Verify issues exist:")
        print("           python verify_issues.py")
        print()
        print("  Step 2 — Start self-healing system:")
        print("           python realtime_self_healing_mongodb.py")
        print()
        print("  Step 3 — Open dashboard:")
        print("           http://localhost:5000")
        print()
        print("  Step 4 — Watch it detect and fix everything in real-time! 🎉")
        print()
        print("  Step 5 — Verify all fixed:")
        print("           python verify_issues.py")
        print()
        print("=" * 70)
        print()
        print("  💡 TIP: Run this script again anytime to recreate all test issues.")
        print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    generator = IssueGenerator()
    generator.generate_all_issues()


if __name__ == '__main__':
    main()

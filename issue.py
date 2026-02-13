#!/usr/bin/env python3
"""
Database Issue Generator for Testing Self-Healing System
Creates intentional errors in MongoDB to test detection and fixing

This script creates:
1. Duplicate records
2. Orphaned documents
3. Missing required fields
4. Invalid data values
5. Slow query scenarios

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
    """Generates test issues in database"""
    
    def __init__(self):
        print("=" * 70)
        print("Database Issue Generator")
        print("Creates test data with intentional errors for testing")
        print("=" * 70)
        print()
        
        try:
            self.client = MongoClient(CONFIG['MONGODB_URI'], serverSelectionTimeoutMS=5000)
            self.db = self.client[CONFIG['DATABASE_NAME']]
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {CONFIG['DATABASE_NAME']}")
            print()
        except Exception as e:
            print(f"❌ Cannot connect to MongoDB: {e}")
            print("Please make sure MongoDB is running!")
            sys.exit(1)
    
    def generate_all_issues(self):
        """Generate all types of issues"""
        
        print("Generating test data with issues...")
        print("=" * 70)
        print()
        
        # Clear existing test data
        self.clear_test_data()
        
        # Create issues
        self.create_duplicate_users()
        self.create_orphaned_orders()
        self.create_users_with_missing_fields()
        self.create_orders_with_invalid_data()
        self.create_data_for_slow_queries()
        
        print()
        print("=" * 70)
        print("✅ Test Issues Created Successfully!")
        print("=" * 70)
        print()
        self.print_summary()
    
    def clear_test_data(self):
        """Clear existing test data"""
        print("🗑️  Clearing existing test data...")
        
        self.db.users.delete_many({})
        self.db.orders.delete_many({})
        self.db.products.delete_many({})
        
        print("   Cleared users, orders, and products collections")
        print()
    
    def create_duplicate_users(self):
        """Create duplicate user records"""
        print("1️⃣  Creating DUPLICATE USERS...")
        
        duplicates = [
            {
                'email': 'john@example.com',
                'name': 'John Doe',
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': 'john@example.com',  # Duplicate!
                'name': 'John Doe',
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': 'john@example.com',  # Duplicate!
                'name': 'John Smith',
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': 'alice@example.com',
                'name': 'Alice Johnson',
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': 'alice@example.com',  # Duplicate!
                'name': 'Alice Johnson',
                'status': 'inactive',
                'created_at': datetime.now()
            },
            {
                'email': 'bob@example.com',
                'name': 'Bob Wilson',
                'status': 'active',
                'created_at': datetime.now()
            }
        ]
        
        result = self.db.users.insert_many(duplicates)
        
        print(f"   ✅ Created {len(result.inserted_ids)} users")
        print(f"   ⚠️  Duplicates: john@example.com (3 times), alice@example.com (2 times)")
        print()
    
    def create_orphaned_orders(self):
        """Create orders that reference non-existent users"""
        print("2️⃣  Creating ORPHANED ORDERS...")
        
        orders = [
            {
                'order_id': 'ORD-001',
                'user_email': 'bob@example.com',  # Valid user
                'product': 'Laptop',
                'amount': 999.99,
                'status': 'pending',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-002',
                'user_email': 'nonexistent@example.com',  # Orphaned! User doesn't exist
                'product': 'Mouse',
                'amount': 29.99,
                'status': 'completed',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-003',
                'user_email': 'deleted_user@example.com',  # Orphaned! User doesn't exist
                'product': 'Keyboard',
                'amount': 79.99,
                'status': 'pending',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-004',
                'user_email': 'alice@example.com',  # Valid user (duplicate, but exists)
                'product': 'Monitor',
                'amount': 299.99,
                'status': 'processing',
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-005',
                'user_email': 'ghost@example.com',  # Orphaned! User doesn't exist
                'product': 'Webcam',
                'amount': 59.99,
                'status': 'cancelled',
                'created_at': datetime.now()
            }
        ]
        
        result = self.db.orders.insert_many(orders)
        
        print(f"   ✅ Created {len(result.inserted_ids)} orders")
        print(f"   ⚠️  Orphaned orders: 3 (users don't exist)")
        print(f"      - nonexistent@example.com")
        print(f"      - deleted_user@example.com")
        print(f"      - ghost@example.com")
        print()
    
    def create_users_with_missing_fields(self):
        """Create users with missing required fields"""
        print("3️⃣  Creating USERS WITH MISSING FIELDS...")
        
        incomplete_users = [
            {
                # Missing 'email' field!
                'name': 'Charlie Brown',
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': '',  # Empty email!
                'name': 'Diana Prince',
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'email': None,  # Null email!
                'name': 'Eve Adams',
                'status': 'inactive',
                'created_at': datetime.now()
            },
            {
                'email': 'frank@example.com',
                # Missing 'name' field!
                'status': 'active',
                'created_at': datetime.now()
            }
        ]
        
        result = self.db.users.insert_many(incomplete_users)
        
        print(f"   ✅ Created {len(result.inserted_ids)} incomplete users")
        print(f"   ⚠️  Missing fields:")
        print(f"      - 1 user without email")
        print(f"      - 1 user with empty email")
        print(f"      - 1 user with null email")
        print(f"      - 1 user without name")
        print()
    
    def create_orders_with_invalid_data(self):
        """Create orders with invalid status values"""
        print("4️⃣  Creating ORDERS WITH INVALID DATA...")
        
        invalid_orders = [
            {
                'order_id': 'ORD-101',
                'user_email': 'bob@example.com',
                'product': 'Tablet',
                'amount': 399.99,
                'status': 'xyz',  # Invalid! Should be pending/processing/completed/cancelled
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-102',
                'user_email': 'alice@example.com',
                'product': 'Phone',
                'amount': 699.99,
                'status': 'unknown',  # Invalid!
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-103',
                'user_email': 'john@example.com',
                'product': 'Headphones',
                'amount': 149.99,
                'status': 'in_progress',  # Invalid! Should be 'processing'
                'created_at': datetime.now()
            },
            {
                'order_id': 'ORD-104',
                'user_email': 'bob@example.com',
                'product': 'Charger',
                'amount': 19.99,
                'status': 'done',  # Invalid! Should be 'completed'
                'created_at': datetime.now()
            }
        ]
        
        result = self.db.orders.insert_many(invalid_orders)
        
        print(f"   ✅ Created {len(result.inserted_ids)} orders with invalid data")
        print(f"   ⚠️  Invalid statuses:")
        print(f"      - 'xyz' (should be pending/processing/completed/cancelled)")
        print(f"      - 'unknown'")
        print(f"      - 'in_progress'")
        print(f"      - 'done'")
        print()
    
    def create_data_for_slow_queries(self):
        """Create data that will cause slow queries"""
        print("5️⃣  Creating DATA FOR SLOW QUERIES...")
        
        # Create many products without indexes
        products = []
        for i in range(1000):
            products.append({
                'product_id': f'PROD-{i:04d}',
                'name': f'Product {i}',
                'category': random.choice(['Electronics', 'Clothing', 'Books', 'Food', 'Toys']),
                'price': round(random.uniform(10, 1000), 2),
                'stock': random.randint(0, 100),
                'description': f'This is product number {i} with a long description that makes queries slower',
                'created_at': datetime.now() - timedelta(days=random.randint(0, 365))
            })
        
        result = self.db.products.insert_many(products)
        
        print(f"   ✅ Created {len(result.inserted_ids)} products")
        print(f"   ⚠️  No indexes created (will cause slow queries)")
        print(f"      - Queries on 'category' will be slow")
        print(f"      - Queries on 'price' will be slow")
        print()
    
    def print_summary(self):
        """Print summary of created issues"""
        print("📊 SUMMARY OF ISSUES CREATED:")
        print()
        
        # Count issues
        total_users = self.db.users.count_documents({})
        total_orders = self.db.orders.count_documents({})
        total_products = self.db.products.count_documents({})
        
        print(f"Total Documents Created:")
        print(f"  • Users: {total_users}")
        print(f"  • Orders: {total_orders}")
        print(f"  • Products: {total_products}")
        print()
        
        print(f"Issues Created:")
        print(f"  1. Duplicate Records:")
        print(f"     ⚠️  john@example.com appears 3 times")
        print(f"     ⚠️  alice@example.com appears 2 times")
        print()
        
        print(f"  2. Orphaned Documents:")
        print(f"     ⚠️  3 orders reference non-existent users")
        print()
        
        print(f"  3. Missing Required Fields:")
        print(f"     ⚠️  4 users with missing/empty/null emails or names")
        print()
        
        print(f"  4. Invalid Data:")
        print(f"     ⚠️  4 orders with invalid status values")
        print()
        
        print(f"  5. Slow Query Potential:")
        print(f"     ⚠️  1000 products without indexes")
        print()
        
        print("=" * 70)
        print()
        print("🚀 NOW RUN THE SELF-HEALING SYSTEM:")
        print("   python realtime_self_healing_mongodb.py")
        print()
        print("📊 THEN OPEN THE DASHBOARD:")
        print("   http://localhost:5000")
        print()
        print("👀 WATCH IT DETECT AND FIX THESE ISSUES IN REAL-TIME!")
        print("=" * 70)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    generator = IssueGenerator()
    generator.generate_all_issues()
    
    print()
    print("💡 TIP: Run this script again anytime to recreate test issues")
    print()

if __name__ == '__main__':
    main()

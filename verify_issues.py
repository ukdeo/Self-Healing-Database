#!/usr/bin/env python3
"""
Issue Verification Script
Checks what issues exist in the database and shows what will be detected

Usage: python verify_issues.py
"""

from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
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
        print("Database Issue Verification Tool")
        print("Shows what issues exist in your database")
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
            sys.exit(1)
    
    def verify_all(self):
        """Verify all issues"""
        
        print("Scanning database for issues...")
        print("=" * 70)
        print()
        
        total_issues = 0
        
        # Check each type
        total_issues += self.check_duplicates()
        total_issues += self.check_orphaned()
        total_issues += self.check_missing_fields()
        total_issues += self.check_invalid_data()
        total_issues += self.check_indexes()
        
        print()
        print("=" * 70)
        print(f"📊 TOTAL ISSUES FOUND: {total_issues}")
        print("=" * 70)
        print()
        
        if total_issues > 0:
            print("🔧 These issues will be detected by the self-healing system!")
            print()
            print("To see them being fixed in real-time:")
            print("  1. Run: python realtime_self_healing_mongodb.py")
            print("  2. Open: http://localhost:5000")
            print("  3. Watch the dashboard as it detects and fixes!")
        else:
            print("✅ No issues found! Your database is clean.")
            print()
            print("To create test issues:")
            print("  python create_test_issues.py")
        
        print()
    
    def check_duplicates(self):
        """Check for duplicate records"""
        print("1️⃣  DUPLICATE RECORDS")
        print("-" * 70)
        
        count = 0
        
        try:
            # Check for duplicate emails
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
                    count += dup['count'] - 1  # Count extras
                    print(f"   ⚠️  Email: {dup['_id']}")
                    print(f"      Appears: {dup['count']} times")
                    print(f"      IDs: {[str(id) for id in dup['ids']]}")
                    print()
            else:
                print("   ✅ No duplicates found")
                print()
        
        except Exception as e:
            print(f"   ❌ Error checking duplicates: {e}")
            print()
        
        return count
    
    def check_orphaned(self):
        """Check for orphaned documents"""
        print("2️⃣  ORPHANED DOCUMENTS")
        print("-" * 70)
        
        count = 0
        
        try:
            # Get valid user emails
            if 'users' in self.db.list_collection_names():
                valid_emails = set(
                    doc.get('email') for doc in self.db.users.find({}, {'email': 1})
                    if doc.get('email')
                )
            else:
                valid_emails = set()
            
            # Check orders
            if 'orders' in self.db.list_collection_names():
                for order in self.db.orders.find():
                    user_email = order.get('user_email')
                    if user_email and user_email not in valid_emails:
                        count += 1
                        print(f"   ⚠️  Order: {order.get('order_id', order['_id'])}")
                        print(f"      User email: {user_email} (doesn't exist)")
                        print()
            
            if count == 0:
                print("   ✅ No orphaned documents found")
                print()
        
        except Exception as e:
            print(f"   ❌ Error checking orphaned docs: {e}")
            print()
        
        return count
    
    def check_missing_fields(self):
        """Check for missing required fields"""
        print("3️⃣  MISSING REQUIRED FIELDS")
        print("-" * 70)
        
        count = 0
        
        try:
            # Check users without email
            missing_email = list(self.db.users.find({
                '$or': [
                    {'email': {'$exists': False}},
                    {'email': None},
                    {'email': ''}
                ]
            }))
            
            for user in missing_email:
                count += 1
                print(f"   ⚠️  User ID: {user['_id']}")
                print(f"      Missing: email field")
                print(f"      Name: {user.get('name', 'N/A')}")
                print()
            
            # Check users without name
            missing_name = list(self.db.users.find({
                '$or': [
                    {'name': {'$exists': False}},
                    {'name': None},
                    {'name': ''}
                ]
            }))
            
            for user in missing_name:
                if user not in missing_email:  # Don't count twice
                    count += 1
                    print(f"   ⚠️  User ID: {user['_id']}")
                    print(f"      Missing: name field")
                    print(f"      Email: {user.get('email', 'N/A')}")
                    print()
            
            if count == 0:
                print("   ✅ No missing fields found")
                print()
        
        except Exception as e:
            print(f"   ❌ Error checking missing fields: {e}")
            print()
        
        return count
    
    def check_invalid_data(self):
        """Check for invalid data values"""
        print("4️⃣  INVALID DATA VALUES")
        print("-" * 70)
        
        count = 0
        
        try:
            # Check for invalid order statuses
            valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
            
            invalid_orders = list(self.db.orders.find({
                'status': {'$nin': valid_statuses}
            }))
            
            for order in invalid_orders:
                count += 1
                print(f"   ⚠️  Order: {order.get('order_id', order['_id'])}")
                print(f"      Invalid status: '{order.get('status')}'")
                print(f"      Valid values: {', '.join(valid_statuses)}")
                print()
            
            if count == 0:
                print("   ✅ No invalid data found")
                print()
        
        except Exception as e:
            print(f"   ❌ Error checking invalid data: {e}")
            print()
        
        return count
    
    def check_indexes(self):
        """Check for missing indexes"""
        print("5️⃣  MISSING INDEXES")
        print("-" * 70)
        
        count = 0
        
        try:
            # Check products collection
            if 'products' in self.db.list_collection_names():
                indexes = list(self.db.products.list_indexes())
                index_fields = set()
                
                for idx in indexes:
                    index_fields.update(idx.get('key', {}).keys())
                
                doc_count = self.db.products.count_documents({})
                
                if doc_count > 100:  # Significant number of docs
                    # Check for common query fields
                    recommended_indexes = ['category', 'price', 'name']
                    
                    for field in recommended_indexes:
                        if field not in index_fields:
                            count += 1
                            print(f"   ⚠️  Collection: products")
                            print(f"      Missing index on: {field}")
                            print(f"      Document count: {doc_count}")
                            print(f"      Recommendation: db.products.createIndex({{{field}: 1}})")
                            print()
            
            if count == 0:
                print("   ✅ No critical missing indexes")
                print()
        
        except Exception as e:
            print(f"   ❌ Error checking indexes: {e}")
            print()
        
        return count
    
    def get_database_stats(self):
        """Get overall database statistics"""
        print()
        print("=" * 70)
        print("📊 DATABASE STATISTICS")
        print("=" * 70)
        
        try:
            stats = self.db.command('dbStats')
            
            print(f"Database: {CONFIG['DATABASE_NAME']}")
            print(f"Collections: {stats.get('collections', 0)}")
            print(f"Data Size: {stats.get('dataSize', 0) / (1024*1024):.2f} MB")
            print(f"Index Size: {stats.get('indexSize', 0) / (1024*1024):.2f} MB")
            print()
            
            # List collections with counts
            print("Collections:")
            for coll_name in self.db.list_collection_names():
                if not coll_name.startswith('system.'):
                    count = self.db[coll_name].count_documents({})
                    print(f"  • {coll_name}: {count} documents")
            
        except Exception as e:
            print(f"Error getting stats: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    verifier = IssueVerifier()
    verifier.verify_all()
    verifier.get_database_stats()
    
    print()

if __name__ == '__main__':
    main()

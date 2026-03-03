#!/usr/bin/env python3
"""
Test database connection and basic operations
"""

import os
from dotenv import load_dotenv
from src.database import get_db
from src.models import Account, Video, Proxy

# Load environment variables
load_dotenv()

def test_database():
    """Test database connection and basic operations"""
    
    try:
        # Get database session
        db = next(get_db())
        
        print("Testing database connection...")
        
        # Test 1: Get count of existing accounts
        existing_accounts = db.query(Account).count()
        print(f"Existing accounts: {existing_accounts}")
        
        # Test 2: Add a test proxy if none exist
        proxy_count = db.query(Proxy).count()
        if proxy_count == 0:
            test_proxy = Proxy(
                address="http://127.0.0.1:8080",
                username="test_user",
                password="test_password",
                country="Test Country"
            )
            db.add(test_proxy)
            db.commit()
            print("Test proxy added")
        else:
            print(f"Existing proxies: {proxy_count}")
        
        # Test 3: Verify proxy was added
        proxies = db.query(Proxy).all()
        for proxy in proxies:
            print(f"Proxy: {proxy.address} ({proxy.country})")
        
        # Test 4: Check if tables are created
        print("\nTables in database:")
        tables = []
        for mapper in Account.__mapper__.registry.mappers:
            tables.append(mapper.class_.__tablename__)
        
        for table in sorted(tables):
            print(f"  - {table}")
        
        print("\nOK Database test completed successfully")
        
    except Exception as e:
        print(f"\nERROR Database test failed: {e}")
        import traceback
        print(traceback.format_exc())
        
    finally:
        # Close the session
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    test_database()

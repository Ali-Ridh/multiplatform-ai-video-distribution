#!/usr/bin/env python3
"""
Script to create all database tables
"""

import sys
import os
from src.database import engine, Base

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all models so they are registered with Base.metadata
import src.models

def create_all_tables():
    """Create all database tables based on models"""
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("All database tables created successfully")
        
        # Print table names
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
        return True
        
    except Exception as e:
        print(f"Failed to create tables: {e}")
        return False

if __name__ == "__main__":
    create_all_tables()

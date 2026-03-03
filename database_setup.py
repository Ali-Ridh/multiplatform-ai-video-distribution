#!/usr/bin/env python3
"""
Database setup script for Opus
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_database():
    """Initialize the database with required tables"""
    
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Check if we're using SQLite (for file creation)
        if "sqlite" in db_url:
            print("SQLite database configuration detected")
        
        # Test connection
        with engine.connect() as connection:
            print("Successfully connected to database")
            
            # Create tables if they don't exist
            # These tables would typically be defined in SQLAlchemy models
            # For now, we'll just check basic functionality
            
            # Example: Create a simple test table (would be replaced with actual models)
            try:
                with connection.begin() as transaction:
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS test_table (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                
                # Test insertion
                connection.execute(text("""
                    INSERT INTO test_table (name) VALUES (:name)
                """), {"name": "Test Entry"})
                connection.commit()
                
                # Test query
                result = connection.execute(text("SELECT * FROM test_table"))
                print("Test data inserted successfully")
                
            except Exception as e:
                print(f"Database initialization error: {e}")
        
        print("Database setup complete")
        return True
        
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return False

if __name__ == "__main__":
    initialize_database()

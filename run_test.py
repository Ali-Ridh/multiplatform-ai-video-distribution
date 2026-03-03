#!/usr/bin/env python3
"""
Run database test with proper Python path
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test.test_database import test_database

if __name__ == "__main__":
    test_database()

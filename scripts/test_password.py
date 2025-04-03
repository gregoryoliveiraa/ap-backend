#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
from passlib.context import CryptContext

# Direct access to database without loading app modules
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to the database
conn = sqlite3.connect('../app.db')
cursor = conn.cursor()

# Get admin user
cursor.execute("SELECT email, senha_hash FROM usuarios WHERE email=?", ["admin@example.com"])
user = cursor.fetchone()

if user:
    email, stored_hash = user
    print(f"User: {email}")
    print(f"Stored hash: {stored_hash}")
    
    # Test with the correct password
    plain_password = "admin123"
    try:
        verification_result = pwd_context.verify(plain_password, stored_hash)
        print(f"Password verification for '{plain_password}': {verification_result}")
    except Exception as e:
        print(f"Error verifying password: {str(e)}")
    
    # Try to hash a password directly
    try:
        new_hash = pwd_context.hash(plain_password)
        print(f"New hash for '{plain_password}': {new_hash}")
        
        # Verify the new hash
        verify_new = pwd_context.verify(plain_password, new_hash)
        print(f"Verification of new hash: {verify_new}")
    except Exception as e:
        print(f"Error hashing password: {str(e)}")
    
else:
    print("Admin user not found in database")

conn.close() 
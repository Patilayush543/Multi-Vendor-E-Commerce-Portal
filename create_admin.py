#!/usr/bin/env python
"""
Script to create a superuser admin account for Patilcraft
Usage: python create_admin.py
"""

import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ECommerce.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Define admin credentials
ADMIN_USERNAME = 'ayush'
ADMIN_EMAIL = 'ayush@example.com'
ADMIN_PASSWORD = 'Pass@123'

# Check if the admin user already exists
if User.objects.filter(username=ADMIN_USERNAME).exists():
    print(f"User '{ADMIN_USERNAME}' already exists.")
else:
    # Create the superuser
    User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print("ADMIN_CREATED")

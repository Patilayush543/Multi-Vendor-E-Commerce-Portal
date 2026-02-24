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
ADMIN_PASSWORD = 'Pass@543'

# Check if the admin user already exists
user, created = User.objects.get_or_create(
    username=ADMIN_USERNAME,
    defaults={
        'email': ADMIN_EMAIL,
        'is_staff': True,
        'is_superuser': True,
    }
)

# Ensure user has admin permissions
if not created:
    user.is_staff = True
    user.is_superuser = True
    user.email = ADMIN_EMAIL
    user.save()
    print(f"User '{ADMIN_USERNAME}' updated with admin permissions.")
else:
    # Set password for newly created user
    user.set_password(ADMIN_PASSWORD)
    user.save()
    print("ADMIN_CREATED")

print(f"Admin account ready: username='{ADMIN_USERNAME}', is_staff={user.is_staff}, is_superuser={user.is_superuser}")

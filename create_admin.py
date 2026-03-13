#!/usr/bin/env python
"""
Power-User Script: Forces 'ayush' admin account with all permissions
This script FORCES the user 'ayush' to be a Super Admin with all doors open
Usage: python create_admin.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ECommerce.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# determine credentials from environment (useful in CI or production)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'ayush')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Pass@123')

# This script FORCES the named user to be a Super Admin
user, created = User.objects.get_or_create(username=ADMIN_USERNAME)
user.set_password(ADMIN_PASSWORD)
user.is_staff = True
user.is_superuser = True
user.is_active = True  # Makes sure the account isn't disabled
user.save()

if created:
    print("POWER_USER_CREATED")
else:
    print("POWER_USER_PERMISSIONS_UPDATED")

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

# This script FORCES the user 'ayush' to be a Super Admin
user, created = User.objects.get_or_create(username='ayush')
user.set_password('Pass@123')
user.is_staff = True
user.is_superuser = True
user.is_active = True  # Makes sure the account isn't disabled
user.save()

if created:
    print("POWER_USER_CREATED")
else:
    print("POWER_USER_PERMISSIONS_UPDATED")

#!/bin/bash
# Build script for Render deployment

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# ensure an admin user exists (optional credentials via env vars)
python create_admin.py || echo "create_admin failed, continuing"

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully!"

#!/bin/bash
set -e

echo "=== School Management System - Build Script ==="

echo "Step 1: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 2: Installing Node.js dependencies..."
npm install || true

echo "Step 3: Building Tailwind CSS..."
npm run build:tailwind || true

echo "Step 4: Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Step 5: Running database migrations..."
python manage.py migrate --noinput || true

echo "Step 6: Creating default admin accounts..."
python manage.py create_default_admins || true

echo "Step 7: Initialize ECD class profiles (if any)"
python manage.py init_ecd_profiles || true

echo "=== Build Complete ==="

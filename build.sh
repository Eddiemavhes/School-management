#!/bin/bash
set -e

echo "=== School Management System - Build Script ==="

echo "Step 1: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Step 3: Running database migrations..."
python manage.py migrate --noinput || true

echo "=== Build Complete ==="

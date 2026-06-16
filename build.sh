#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
flask db upgrade 2>/dev/null || python -c "from app import app; from models import db; app.app_context().__enter__(); db.create_all()"

echo "Seeding database..."
python seed.py

echo "Build complete!"

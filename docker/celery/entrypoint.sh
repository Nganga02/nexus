#!/bin/bash
set -e

# Optionally run Django migrations (optional, if web handles it)
# python manage.py migrate

# Start Celery worker
exec celery -A project worker -l info

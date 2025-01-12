#!/usr/bin/env bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Run Django commands
python manage.py collectstatic --noinput
python manage.py migrate

#!/bin/bash

cd isms

# Create venv only if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

source venv/bin/activate

# Install dependencies quietly
pip install -q -r requirements.txt

# Change to the inner isms directory where manage.py is located
cd isms

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
# Retail Auto Parts System
CSCE 4350 Database Systems — Team project (Retail Auto Parts System).

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, PostgreSQL
- **Frontend**: Django templates (HTML/CSS), simple JS fetch for login
- **Database**: PostgreSQL

## Setup

1. Clone the repo and go into the backend:

   ```bash
   git clone <your-repo-url>
   cd retail-auto-parts-system-main/backend

2. Create a Python virtual enviroment
    - python3 -m venv .venv
    
    For MacOS/Linux:
    - source .venv/bin/activate

    For Windows (Powershell)
    - .venv/Scripts/Activate.ps1

3. Install required packages
    ```bash
    pip install -r -requirements.txt

4. Apply Database Migrations
    ```bash
    python3 managae.py migrate


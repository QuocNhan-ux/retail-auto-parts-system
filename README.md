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

    ```bash
    python3 -m venv .venv
    
To activate it for MacOS/Linux:
    source .venv/bin/activate

To activate it for Windows (Powershell):
    ```bash
    .venv/Scripts/Activate.ps1

3. Install required packages
    ```bash
    pip install -r -requirements.txt

4. Apply Database Migrations and Deploy
    ```bash
    python3 managae.py migrate

Create Administrator Access:
    bash
    python3 manage.py createsuperuser
    python3 manage.py runserver

5. Access the App
Home Page:
http://127.0.0.1:8000/

Customer Login:
http://127.0.0.1:8000/customer/login/

Employee Login:
http://127.0.0.1:8000/employee/login/

Admin Panel (superuser only):
http://127.0.0.1:8000/admin/


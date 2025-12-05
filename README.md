# Retail Auto Parts System
CSCE 4350 Database Systems — Team project (Retail Auto Parts System).

The Project Reports contain reports generated during each phase of the project, documenting the team's progress throughout the semester while developing the Retail Auto Parts System

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, PostgreSQL
- **Frontend**: Django templates (HTML/CSS), simple JS fetch for login
- **Database**: PostgreSQL

## Setup

1. Clone the repo and go into the backend:

   ```bash
   git clone <your-repo-url>
   cd retail-auto-parts-system-main/
   ```

2. Create a Python virtual enviroment

    ```bash
    python3 -m venv .venv
    ```
    To activate it for MacOS/Linux:
    ```bash
    source .venv/bin/activate
    ```
    To activate it for Windows (Powershell):
    ```bash
    .venv/Scripts/Activate.ps1
    ```

3. Install required packages

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

4. Apply Database Migrations and Deploy

    ```bash
    python3 manage.py migrate
    ```
    
    To gain Admin access: (Enter any username, email, password) 
    login at http://127.0.0.1:8000/admin/
    ```bash
    python3 manage.py createsuperuser
    ```
    
    Launch application from backend/
    ```bash
    python3 manage.py runserver
    ```

5. Access Webpage:

Home Page:
http://127.0.0.1:8000/

Customer Login:
http://127.0.0.1:8000/customer/login/

Employee Login:
http://127.0.0.1:8000/employee/login/

Admin Panel (superuser only):
http://127.0.0.1:8000/admin/


## Getting Started

1. Access the Django Admin Panel: 
    ```bash
    http://127.0.0.1:8000/admin/
    ```
2. Create a Customer Account

Inside the admin dashboard:
  1. Click Customers
  2. Select Add Customer
  3. Fill all required fields (name, email, username, password, etc.)
  4. Save the new customer record.

This account will be used to sign in on the customer-facing website.

3. Log in as Customer

After adding in some parts:
1. Log out of the admin panel
2. visit the customer login page:
    ```bash
    http://127.0.0.1:8000/customer/login/
    ```
3. sign in using the customer credentials you created

5. Start using the application

once logged in the customer can:
- Browse and search auto parts
- Filter by category or condition
- View products detals
- Add items to cart
- Complete purchases
- Review previous order history


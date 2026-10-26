# OCR Management System - Django Project

## Prerequisites

Before running this project, ensure you have:

1. **Python 3.9 or higher** - Download from https://python.org or Microsoft Store
2. **Django** - Install via pip

## Installation Steps

### 1. Install Python

Download and install Python from:
- https://www.python.org/downloads/
- Or: `ms-windows-store://pdp/?productid=9NJ46SX7X90P`

### 2. Install Django

Open a terminal/command prompt and run:
```bash
pip install django
```

### 3. Navigate to Project Directory

```bash
cd c:\Project\ocr_final
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### Email and secret-key configuration

Set `DJANGO_SECRET_KEY` to a unique secret for deployments. To send email, set
`EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in the environment before starting
the server. Do not commit these values or your local `.env` file.

### 5. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and visit:
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
ocr_final/
├── accounts/          # User authentication app
│   ├── models.py     # Custom user, Student, Landlord models
│   ├── views.py      # Authentication views
│   ├── forms.py      # Registration forms
│   └── urls.py       # URL routing
├── properties/       # Property management app
│   ├── models.py     # Property, Application, Allocation, Review, Message models
│   ├── views.py      # Property management views
│   ├── forms.py      # Property forms
│   └── urls.py       # URL routing
├── ocr_project/      # Main Django project settings
│   ├── settings.py   # Project configuration
│   ├── urls.py       # Main URL configuration
│   └── wsgi.py       # WSGI configuration
├── templates/        # HTML templates
│   ├── base.html     # Base template
│   ├── accounts/     # Login/Register templates
│   ├── students/    # Student dashboard
│   ├── landlords/   # Landlord dashboard
│   └── admin/       # Admin dashboard
├── manage.py         # Django management script
└── README.md         # This file
```

## User Credentials

### Student Registration
- Must use email ending with `@hcuc.edu.gh`
- Login: Email + Password

### Landlord Registration
- Register with name, email, phone
- Receive auto-generated unique code
- Login: Unique Code + Password

### Administrator
- Created via createsuperuser command
- Full system access

## Features Implemented

1. **Role-based Authentication**
   - Custom user model with roles (student, landlord, admin)
   - Email domain validation for students
   - Auto-generated unique code for landlords

2. **Property Management**
   - CRUD operations for property listings
   - Image upload support
   - Approval workflow (admin verification)

3. **Application System**
   - Student booking requests
   - Landlord approval/rejection
   - Room allocation tracking

4. **Messaging System**
   - Direct communication between students and landlords

5. **Security**
   - Password hashing (Django's built-in)
   - CSRF protection
   - Role-based access control
   - SQL injection prevention (ORM)

## Technology Stack

- Python 3.9+
- Django 4.x
- SQLite (default database)
- HTML/CSS/JavaScript
- Bootstrap 5 (for responsive UI)

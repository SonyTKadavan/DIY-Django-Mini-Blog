# Django Blog Project

A feature-rich blog application built with Django that supports user authentication, commenting system, and author profiles.

## Features

- Blog post listing with pagination
- Author profiles and listings
- Comment system with user authentication
- Admin interface for content management
- Responsive design

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to view the blog.

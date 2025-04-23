# Seminar Hall Management System

A comprehensive web application for managing seminar halls and event spaces, built with Django.

## Features

- **User Authentication**
  - User Registration
  - Admin Login
  - OAuth Integration
  - Password Reset

- **User Management**
  - User Profiles
  - Booking History
  - Notifications
  - Reviews

- **Venue Management**
  - Manage Seminar Halls
  - Approve Bookings
  - Set Availability
  - Pricing Management

- **Booking System**
  - Search Venues
  - Filter by Location/Capacity/Price
  - Scheduling
  - Payment Processing

- **Notifications**
  - Email/SMS Alerts
  - Real-time Chat System
  - Booking Status Updates

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, HTML, CSS, JavaScript
- **Database**: SQLite (default), can be configured for PostgreSQL
- **Authentication**: Django AllAuth
- **Notifications**: Django Notifications

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/seminar-hall-system.git
   cd seminar-hall-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## User Types

1. **Regular Users**
   - Can search and book venues
   - Can view booking history
   - Can leave reviews

2. **Venue Managers**
   - Can add and manage venues
   - Can approve or reject booking requests
   - Can set venue availability and pricing

3. **Administrators**
   - Have full access to all features
   - Can manage users and their permissions
   - Can access the Django admin interface

## Project Structure

- `accounts/`: User authentication and profile management
- `venues/`: Venue management and search functionality
- `bookings/`: Booking and payment processing
- `notifications_app/`: Notification and chat system
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, images)
- `media/`: User-uploaded files

## Acknowledgements

- Django
- Bootstrap
- Font Awesome
- Django AllAuth
- Django Notifications
- Django Channels 

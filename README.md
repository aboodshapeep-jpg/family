# Family Platform Admin System

A comprehensive Flask-based family management platform with admin controls, user management, and activity logging.

## Features

- **Admin Dashboard**: Real-time statistics and system overview
- **User Management**: Create, edit, and delete user accounts
- **Role-Based Access Control**: Admin, User, and Guest roles
- **Activity Logging**: Comprehensive audit trail of all system activities
- **Authentication**: Secure login with Flask-Login
- **Password Management**: Admin can reset user passwords
- **User Filtering**: Search and filter users by multiple criteria
- **Responsive UI**: Bootstrap 5 based modern interface

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aboodshapeep-jpg/family.git
   cd family
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -c "from main import create_app; app = create_app(); app.app_context().push()"
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

   The application will be available at `http://localhost:5000`

## Default Setup

- **Admin Dashboard**: `/admin/dashboard`
- **Manage Users**: `/admin/users`
- **Add User**: `/admin/add-user`
- **Activity Logs**: `/admin/activity-logs`

## Creating the First Admin Account

1. Visit `http://localhost:5000/auth/register-admin`
2. Fill in the admin account details
3. Click "Create Admin Account"
4. Use the credentials to login

## Project Structure

```
family/
├── admin/
│   └── routes.py              # Admin dashboard routes
├── auth/
│   └── routes.py              # Authentication routes
├── templates/
│   ├── base.html              # Base template
│   ├── navbar.html            # Navigation bar
│   ├── admin_sidebar.html     # Admin sidebar
│   ├── flash_messages.html    # Flash message component
│   ├── footer.html            # Footer
│   ├── auth/
│   │   ├── login.html         # Login page
│   │   └── register_admin.html # Admin registration
│   ├── admin/
│   │   ├── dashboard.html     # Admin dashboard
│   │   ├── users.html         # User management
│   │   ├── add_user.html      # Add user form
│   │   ├── edit_user.html     # Edit user form
│   │   └── activity_logs.html # Activity logs
│   └── errors/
│       ├── 404.html           # 404 error page
│       ├── 403.html           # 403 error page
│       └── 500.html           # 500 error page
├── models.py                  # Database models
├── config.py                  # Configuration settings
├── main.py                    # Application factory
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Database Models

### User Model
- Username (unique)
- Email (unique)
- Password (hashed)
- First Name
- Last Name
- Role (FK to Role)
- Active Status
- Timestamps (created_at, updated_at)
- Last Login

### Role Model
- Name (unique)
- Description

### ActivityLog Model
- User (FK to User)
- Action
- Description
- IP Address
- User Agent
- Timestamp

### FamilyMember Model
- User (FK to User)
- Name
- Relationship
- Date of Birth
- Timestamps

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Secure session cookies
- Admin-only route protection
- Activity logging for audit trail
- SQL injection prevention with SQLAlchemy ORM

## Configuration

### Environment Variables

```
FLASK_ENV=development          # development, production, testing
FLASK_APP=main.py
SECRET_KEY=your-secret-key     # Change in production!
DATABASE_URL=sqlite:///family.db
SESSION_COOKIE_SECURE=False    # Set to True in production
REMEMBER_COOKIE_SECURE=False   # Set to True in production
```

## API Routes

### Authentication
- `GET /auth/login` - Login page
- `POST /auth/login` - Process login
- `GET /auth/register-admin` - Admin registration page
- `POST /auth/register-admin` - Create admin account
- `GET /auth/logout` - Logout user

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management page
- `GET /admin/add-user` - Add user form
- `POST /admin/add-user` - Create new user
- `GET /admin/user/<id>/edit` - Edit user form
- `POST /admin/user/<id>/edit` - Save user changes
- `POST /admin/user/<id>/delete` - Delete user
- `POST /admin/user/<id>/reset-password` - Reset user password
- `GET /admin/activity-logs` - View activity logs

## Development

For development, the application uses SQLite by default. To use PostgreSQL:

1. Install PostgreSQL
2. Create a database: `createdb family_db`
3. Update `.env`: `DATABASE_URL=postgresql://username:password@localhost:5432/family_db`
4. Install psycopg2: `pip install psycopg2-binary`

## Production Deployment

1. Set `FLASK_ENV=production`
2. Change `SECRET_KEY` to a secure random value
3. Set up PostgreSQL database
4. Set `SESSION_COOKIE_SECURE=True`
5. Use a WSGI server like Gunicorn: `gunicorn main:app`
6. Set up a reverse proxy (Nginx)
7. Enable HTTPS with SSL/TLS certificates

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

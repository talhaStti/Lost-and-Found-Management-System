# Lost and Found Management System

A comprehensive Lost and Found Management System built with Flask and vanilla JavaScript.

## Features

- User registration and authentication
- Report lost and found items with images
- Automatic matching system between lost/found items
- Admin dashboard for match approval/rejection
- Search functionality across all items
- Responsive design with Bootstrap

## Prerequisites

Before running this project locally, make sure you have:

1. **Python 3.7+** installed (Download from https://python.org)
2. **VS Code** (recommended) or any text editor

## Required Files

Make sure you have downloaded all these files from the project:

**Core Files:**
- `app_local.py` (main application file for local development)
- `models.py`, `routes.py`, `forms.py`, `utils.py`
- `local_requirements.txt` (dependencies)
- `.env.example` (environment template)

**Template Files:**
- `templates/` folder with all HTML files
- `static/` folder with CSS and JavaScript files

## Step-by-Step Setup Instructions

### 1. Download Project Files
- Download all project files to a folder on your computer
- Open the folder in VS Code or your preferred editor

### 2. Set Up Python Virtual Environment

Open terminal/command prompt in your project folder:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r local_requirements.txt
```

### 4. Database Setup (Choose One Option)

#### Option A: SQLite (Recommended - No Installation Required)
The system will automatically create a SQLite database file. No setup needed!

#### Option B: PostgreSQL (Advanced)
1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create database and user as shown in advanced setup section below

### 5. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   # On Windows:
   copy .env.example .env
   # On macOS/Linux:
   cp .env.example .env
   ```

2. Edit the `.env` file:
   ```env
   # For SQLite (easiest):
   DATABASE_URL=sqlite:///lost_and_found.db
   
   # For PostgreSQL (if you installed it):
   # DATABASE_URL=postgresql://lostfound:your_password@localhost:5432/lost_and_found
   
   SESSION_SECRET=your-very-long-random-secret-key-change-this
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

### 6. Run the Application

```bash
python app_local.py
```

The application will be available at `http://localhost:5000`

## First Time Usage

1. **Open your browser** and go to `http://localhost:5000`
2. **Register an account** by clicking "Sign Up"
3. **Start using the system** by reporting lost or found items

### Creating an Admin Account

To access admin features:
1. Register a normal account first
2. Stop the application (Ctrl+C)
3. Run this command to make yourself admin:
   ```bash
   python -c "
   from app_local import app, db
   from models import User
   with app.app_context():
       user = User.query.filter_by(email='your-email@example.com').first()
       if user:
           user.is_admin = True
           db.session.commit()
           print('Admin access granted!')
       else:
           print('User not found')
   "
   ```
4. Restart the application: `python app_local.py`

## Project Structure

```
lost-and-found/
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models
├── routes.py           # Application routes
├── forms.py            # WTForms definitions
├── utils.py            # Utility functions
├── static/             # CSS, JS, and images
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/          # HTML templates
│   ├── base.html
│   ├── dashboard/
│   ├── items/
│   └── auth/
└── README.md
```

## Usage

1. **Register an Account**: Create a new user account or use admin credentials
2. **Report Lost Items**: Fill out the form with item details and optional image
3. **Report Found Items**: Submit found items with descriptions
4. **View Matches**: The system automatically finds potential matches
5. **Admin Functions**: Approve/reject matches through the admin dashboard

## Admin Account

To create an admin account:

1. Register a normal account first
2. Access your database and update the user:

```sql
UPDATE "user" SET is_admin = true WHERE email = 'your-email@example.com';
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check your DATABASE_URL in the .env file
- Verify database credentials

### Import Errors
- Make sure your virtual environment is activated
- Install all required packages with pip

### Port Already in Use
- Change the port in main.py if 5000 is occupied
- Or stop other applications using port 5000

## Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python main.py
```

## Production Deployment

For production deployment, consider:
- Using a proper WSGI server like Gunicorn
- Setting up environment variables properly
- Configuring a reverse proxy (nginx)
- Using a production database setup

###  Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/talhaStti/Lost-and-Found-Management-System.git
cd Lost-and-Found-Management-System


## License

This project is for educational purposes

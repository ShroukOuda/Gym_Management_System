# Gym Management System

A comprehensive web application for managing gym operations, including member management, trainer scheduling, equipment tracking, and more.

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.6 or higher
- MySQL server
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/ShroukOuda/Gym_Management_System.git
cd  Gym_Management_System
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up the database**

Create a MySQL database named `gym_management`:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE gym_management;
EXIT;
```

4. **Configure environment variables**

Create a `.env` file in the project root directory:

```
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://root:<your-mysql-password>@localhost/gym_management
```

Replace the password in the DATABASE_URL with your MySQL password.

### Running the Application

1. **Start the Flask application**

```bash
Flask create_tables
Flask create_admin
python app.py
```

2. **Access the application**

Open your web browser and navigate to:
```
http://localhost:5000
```

## Features

- Multi-user role system (Manager, Secretary, Trainer)
- Member management
- Class scheduling
- Equipment tracking
- Package and subscription management
- Reporting and analytics

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, images)
- `config.py`: Application configuration

## Technologies Used

- Flask: Web framework
- SQLAlchemy: ORM for database operations
- Werkzeug: Security and utilities
- PyMySQL: MySQL database connector
- Bootstrap: Frontend framework (optional)

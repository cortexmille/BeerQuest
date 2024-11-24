# Installation and Configuration Guide

## Prerequisites

- Python 3.11 or higher
- PostgreSQL
- A Gmail account for sending notifications
- An OpenAI API key for question synthesis

## Installation

### 1. Clone the project

```bash
git clone https://github.com/cortexmille/BeerQuest.git
cd BeerQuest
```

### 2. Python Dependencies Installation

Required dependencies:
- Flask 3.1.0+
- Flask-SQLAlchemy 3.1.1+
- psycopg2-binary 2.9.10+
- APScheduler 3.10.4+
- OpenAI 1.55.0+
- Flask-Login 0.6.3+
- Flask-Mail 0.10.0+
- WeasyPrint 63.0+
- Flask-APScheduler 1.13.1+
- Flask-SocketIO 5.4.1+
- pytz 2024.2+
- email-validator 2.2.0+

### 3. Environment Configuration

Create a `.env` file at the project root with the following variables:

```env
# Flask
FLASK_SECRET_KEY=your_secret_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database_name

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Email
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_application_password
```

### 4. Database Configuration

1. Create a PostgreSQL database
2. Update the `DATABASE_URL` variable in the `.env` file
3. The database structure will be automatically created on first launch

### 5. Mail Server Configuration

1. Enable 2-factor authentication on your Gmail account
2. Generate an application password
3. Use this password in the `MAIL_PASSWORD` variable

## Starting the Application

1. Launch the application:
```bash
python main.py
```

2. Access the application:
- Public interface: http://localhost:5000
- Admin interface: http://localhost:5000/admin

### Default Administrator Account
- Username: admin
- Email: admin@example.com
- Password: admin123

It is recommended to change these credentials after the first login.

## Features

### Automatic Synthesis
- Question synthesis is performed every 3 minutes
- Uses OpenAI API for analysis
- Results are accessible in the admin dashboard

### Email Notifications
Note: This feature is not yet implemented.
- Automatically sent when new questions are received
- Configuration can be modified in the admin panel

### PDF Export
- Available in the admin panel
- Time period filtering
- Includes original questions and syntheses

## Monitoring and Maintenance

### Logs
- Application logs are available in the console
- Errors are recorded with timestamps

### Performance
- Real-time monitoring in the admin dashboard
- Usage statistics available

## Support

For any questions or issues:
1. Check the error logs
2. Consult the technical documentation
3. Contact the support team

## Security Notes

- Change the default administrator password immediately
- Use strong passwords
- Keep your API keys confidential
- Regularly update dependencies

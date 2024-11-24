from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions import db
from models import Admin
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        try:
            # Check if we need to create the initial superuser
            if not Admin.query.first():
                admin = Admin()
                admin.username = 'admin'
                admin.email = 'admin@example.com'
                admin.set_password('admin123')
                admin.is_superuser = True
                db.session.add(admin)
                db.session.commit()
                print("Created initial superuser admin")
            else:
                # Update existing admin to be superuser if needed
                admin = Admin.query.filter_by(username='admin').first()
                if admin and not admin.is_superuser:
                    admin.is_superuser = True
                    db.session.commit()
                    print("Updated existing admin to superuser")
        except Exception as e:
            db.session.rollback()
            print(f"Error during database initialization: {str(e)}")
            raise

if __name__ == '__main__':
    init_db()

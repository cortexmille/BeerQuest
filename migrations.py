from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions import db
from models import Admin

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()

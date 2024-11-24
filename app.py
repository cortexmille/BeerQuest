import os
from flask import Flask
from flask_migrate import Migrate
from extensions import db, login_manager, mail, scheduler, socketio

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    app.db = db  # Make db accessible through app
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    mail.init_app(app)
    scheduler.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    with app.app_context():
        # Register blueprints
        from routes.public import public_bp
        from routes.admin import admin_bp
        
        app.register_blueprint(public_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # Initialize database
        from migrations import init_db
        init_db()
        
        # Start scheduler
        from tasks import schedule_synthesis
        scheduler.start()
        schedule_synthesis()
        
    return app

app = create_app()

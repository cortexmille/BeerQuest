import os
from flask import Flask
from extensions import db, login_manager, mail, scheduler, socketio

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    app.db = db  # Make db accessible through app
    
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'  # type: ignore
    mail.init_app(app)
    scheduler.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    with app.app_context():
        from models import Admin, Question, Synthesis
        
        def create_default_admin():
            # Vérifier si un admin existe déjà
            if Admin.query.first() is None:
                admin = Admin(
                    username='admin',
                    email='admin@example.com'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Compte administrateur par défaut créé avec succès.")

        db.create_all()
        
        # Créer le compte admin par défaut
        create_default_admin()
        
        # Register blueprints
        from routes.public import public_bp
        from routes.admin import admin_bp
        
        app.register_blueprint(public_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # Start scheduler
        from tasks import schedule_synthesis
        scheduler.start()
        schedule_synthesis()
        
    return app

app = create_app()

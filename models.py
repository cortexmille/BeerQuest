from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    email_notifications = db.Column(db.Boolean, default=True)
    receive_synthesis_copy = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Synthesis(db.Model):
    __tablename__ = 'synthesis'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    archived = db.Column(db.Boolean, default=False)
    archive_date = db.Column(db.DateTime, nullable=True)
    questions = db.relationship('Question', backref='synthesis', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    synthesis_id = db.Column(db.Integer, db.ForeignKey('synthesis.id'), nullable=True)
    
    @staticmethod
    def get_statistics():
        """Calcule les statistiques sur les questions et génère une description détaillée"""
        from sqlalchemy import func
        
        total_questions = Question.query.count()
        processed_questions = Question.query.filter_by(processed=True).count()
        unprocessed_questions = Question.query.filter_by(processed=False).count()
        
        # Statistiques par jour
        questions_by_day = db.session.query(
            func.date(Question.created_at).label('date'),
            func.count(Question.id).label('count')
        ).group_by(func.date(Question.created_at)).all()
        
        # Conversion en format adapté pour Chart.js
        dates = [str(stat.date) for stat in questions_by_day]
        counts = [stat.count for stat in questions_by_day]
        
        # Construction de la description détaillée
        if total_questions == 0:
            transformation_description = "Aucune question n'a encore été soumise au système."
        else:
            processed_percent = (processed_questions / total_questions * 100) if total_questions > 0 else 0
            transformation_description = f"Sur l'ensemble des {total_questions} questions reçues :\n• {processed_questions} questions ({processed_percent:.1f}%) ont été traitées par le LLM\n• {unprocessed_questions} questions sont en attente de traitement\n\nLe processus de transformation comprend :\n1. La modération automatique pour filtrer les contenus inappropriés\n2. L'identification et la fusion des questions similaires\n3. La génération d'une synthèse structurée des questions restantes"
        
        return {
            'total': total_questions,
            'processed': processed_questions,
            'unprocessed': unprocessed_questions,
            'dates': dates,
            'counts': counts,
            'transformation_description': transformation_description
        }
from flask import current_app
from datetime import datetime
import pytz
from models import Question, Synthesis
from utils import generate_synthesis, send_notification_email
from extensions import scheduler, db, socketio

def run_synthesis():
    from app import app
    
    print("Lancement du travail de syntèse...")
    try:
        with app.app_context():
            questions = Question.query.filter_by(processed=False).all()
            print(f"Found {len(questions)} questions non traitées")
            
            if not questions:
                print("Pas de questions à traiter")
                return
                
            # Generate synthesis
            question_texts = [q.content for q in questions]
            synthesis_text = generate_synthesis(question_texts)
            
            if synthesis_text:
                print(f"Synthèse générée par le LLM: {synthesis_text[:100]}...")
                
                # Create synthesis
                synthesis = Synthesis()
                synthesis.content = synthesis_text
                db.session.add(synthesis)
                
                # Update questions
                for question in questions:
                    question.processed = True
                    question.synthesis = synthesis
                
                db.session.commit()
                print("Synthèse sauvegardée avec succès")
                
                # Send notification if enabled
                send_notification_email(synthesis)
                
                # Notify clients to update dashboard
                stats = Question.get_statistics()
                print("Preparing synthesis_complete event data...")
                # Format the event data with all required fields
                event_data = {
                    'success': True,
                    'stats': stats,
                    'new_synthesis': {
                        'content': synthesis.content,
                        'created_at': synthesis.created_at.astimezone(pytz.timezone('Europe/Paris')).strftime('%d/%m/%Y %H:%M:%S %Z'),
                        'id': synthesis.id,
                        'questions': [{'content': q.content} for q in synthesis.questions]
                    }
                }
                
                # Log the event data for debugging
                print(f"Emitting synthesis_complete event with data: {event_data}")
                print(f"Emitting synthesis_complete event with data: {event_data}")
                socketio.emit('synthesis_complete', event_data)
                print("synthesis_complete event emitted successfully")
                
                return True
            else:
                print("No synthesis text generated")
                return False
            
    except Exception as e:
        print(f"Error in run_synthesis: {str(e)}")
        socketio.emit('synthesis_complete', {
            'success': False,
            'error': str(e)
        })
        raise

def schedule_synthesis():
    scheduler.remove_all_jobs()
    scheduler.add_job(
        func=run_synthesis,
        trigger='interval',
        minutes=current_app.config['SYNTHESIS_INTERVAL_MINUTES'],
        id='synthesis_job'
    )

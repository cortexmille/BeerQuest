from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from models import Question

public_bp = Blueprint('public', __name__)

@public_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form.get('question')
        
        if not question:
            flash('Votre question ne peut pas être vide', 'error')
            return redirect(url_for('public.index'))
            
        new_question = Question(content=question)
        db.session.add(new_question)
        db.session.commit()
        
        flash('Votre question a bien été envoyée !', 'success')
        return redirect(url_for('public.index'))
        
    return render_template('index.html')

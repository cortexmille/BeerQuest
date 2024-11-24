from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_user, logout_user, login_required, current_user
from models import Admin, Question, Synthesis
from app import db, scheduler
from datetime import datetime
import os
import pytz

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    print(f"Accessing admin login route - Method: {request.method}")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt for username: {username}")
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            print(f"Successful login for admin: {username}")
            return redirect(url_for('admin.dashboard'))
            
        print("Login failed: Invalid credentials")
        flash('Invalid credentials', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    syntheses = Synthesis.query.filter_by(archived=False).order_by(Synthesis.created_at.desc()).all()
    stats = Question.get_statistics()
    return render_template('admin/dashboard.html', syntheses=syntheses, stats=stats, pytz=pytz)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Mise à jour de l'email et des préférences de notification
        current_user.email = request.form.get('email')
        current_user.email_notifications = 'email_notifications' in request.form
        current_user.receive_synthesis_copy = 'receive_synthesis_copy' in request.form
        
        # Mise à jour de l'intervalle de synthèse
        new_interval = int(request.form.get('synthesis_interval', 60))
        from app import app
        app.config['SYNTHESIS_INTERVAL_MINUTES'] = new_interval
        
        # Redémarrer le job scheduler avec le nouvel intervalle
        from tasks import scheduler, run_synthesis
        scheduler.remove_all_jobs()
        scheduler.add_job(
            func=run_synthesis,
            trigger='interval',
            minutes=new_interval,
            id='synthesis_job'
        )
        
        db.session.commit()
        flash('Paramètres mis à jour avec succès', 'success')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@admin_bp.route('/synthesis/<int:synthesis_id>/pdf')
@login_required
def download_synthesis_pdf(synthesis_id):
    from flask import send_file
    from utils import generate_pdf_synthesis
    import os
    
    synthesis = Synthesis.query.get_or_404(synthesis_id)
    pdf_path = generate_pdf_synthesis(synthesis)
    
    try:
        return send_file(
            pdf_path,
            download_name=f'synthese_{synthesis.created_at.strftime("%Y%m%d_%H%M")}.pdf',
            as_attachment=True
        )
    finally:
        # Supprimer le fichier temporaire après l'envoi
        os.unlink(pdf_path)

@admin_bp.route('/next-run-time')
@login_required
def next_run_time():
    from datetime import datetime, timezone
    job = scheduler.get_job('synthesis_job')
    next_run = job.next_run_time if job else None
    
    # Get pending questions count
    stats = Question.get_statistics()
    
    if next_run:
        time_remaining = next_run - datetime.now(timezone.utc)
        minutes = int(time_remaining.total_seconds() // 60)
        seconds = int(time_remaining.total_seconds() % 60)
        countdown = f"{minutes:02d}:{seconds:02d}"
    else:
        countdown = "--:--"
    
    return {'countdown': countdown, 'pending_questions': stats['unprocessed']}

@admin_bp.route('/run-synthesis', methods=['POST'])
@login_required
def run_synthesis_manual():
    # Vérifier s'il y a des questions en attente
    unprocessed_questions = Question.query.filter_by(processed=False).count()
    if unprocessed_questions == 0:
        return {'success': False, 'error': 'Aucune question en attente de traitement'}
        
    try:
        from tasks import run_synthesis
        run_synthesis()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@admin_bp.route('/statistics')
@login_required
def statistics():
    stats = Question.get_statistics()
    return render_template('admin/statistics.html', stats=stats)

@admin_bp.route('/archives')
@login_required
def archives():
    archived_syntheses = Synthesis.query.filter_by(archived=True).order_by(Synthesis.archive_date.desc()).all()
    return render_template('admin/archives.html', syntheses=archived_syntheses, pytz=pytz)

@admin_bp.route('/synthesis/<int:synthesis_id>/archive', methods=['POST'])
@login_required
def archive_synthesis(synthesis_id):
    try:
        synthesis = Synthesis.query.get_or_404(synthesis_id)
        if synthesis.archived:
            flash('Cette synthèse est déjà archivée.', 'warning')
            return redirect(url_for('admin.dashboard'))
            
        synthesis.archived = True
        synthesis.archive_date = datetime.utcnow()
        db.session.commit()
        flash('Synthèse archivée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'archivage de la synthèse: {str(e)}', 'danger')
        
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/archive-all', methods=['POST'])
@login_required
def archive_all_syntheses():
    try:
        # Récupérer toutes les synthèses non archivées
        syntheses = Synthesis.query.filter_by(archived=False).all()
        
        if not syntheses:
            flash('Aucune synthèse à archiver.', 'info')
            return redirect(url_for('admin.dashboard'))
            
        # Archiver toutes les synthèses
        current_time = datetime.utcnow()
        for synthesis in syntheses:
            synthesis.archived = True
            synthesis.archive_date = current_time
            
        db.session.commit()
        flash(f'{len(syntheses)} synthèses archivées avec succès', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'archivage des synthèses: {str(e)}', 'danger')
        
    return redirect(url_for('admin.dashboard'))
@admin_bp.route('/dashboard/download-all')
@login_required
def download_all_syntheses_pdf():
    from utils import generate_pdf_synthesis
    import tempfile
    from weasyprint import HTML
    from flask import render_template
    
    # Get all active syntheses
    syntheses = Synthesis.query.filter_by(archived=False).order_by(Synthesis.created_at.desc()).all()
    
    if not syntheses:
        flash('Aucune synthèse active à exporter.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    # Generate combined PDF
    html_content = render_template('admin/pdf_synthesis.html', syntheses=syntheses, multiple=True, datetime=datetime)
    
    pdf_file = None
    try:
        pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        HTML(string=html_content).write_pdf(pdf_file.name)
        return send_file(
            pdf_file.name,
            download_name=f'toutes_syntheses_actives_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
            as_attachment=True
        )
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))
    finally:
        if pdf_file and os.path.exists(pdf_file.name):
            os.unlink(pdf_file.name)

@admin_bp.route('/synthesis/<int:synthesis_id>/delete', methods=['POST'])
@login_required
def delete_synthesis(synthesis_id):
    try:
        synthesis = Synthesis.query.filter_by(id=synthesis_id, archived=False).first_or_404()
        db.session.delete(synthesis)
        db.session.commit()
        flash('Synthèse supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la synthèse: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard/delete-all', methods=['POST'])
@login_required
def delete_all_syntheses():
    try:
        # Delete all active syntheses
        syntheses = Synthesis.query.filter_by(archived=False).all()
        if not syntheses:
            flash('Aucune synthèse active à supprimer.', 'info')
            return redirect(url_for('admin.dashboard'))
            
        for synthesis in syntheses:
            db.session.delete(synthesis)
        
        db.session.commit()
        flash('Toutes les synthèses actives ont été supprimées avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression des synthèses: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/archives/download-all-unfiltered')
@login_required
def download_all_archives_unfiltered():
    from utils import generate_pdf_synthesis
    import tempfile
    from weasyprint import HTML
    from flask import render_template
    
    # Get all archived syntheses without date filtering
    syntheses = Synthesis.query.filter_by(archived=True).order_by(Synthesis.archive_date.desc()).all()
    
    if not syntheses:
        flash('Aucune synthèse archivée à exporter.', 'warning')
        return redirect(url_for('admin.archives'))
    
    # Generate combined PDF
    html_content = render_template('admin/pdf_synthesis.html', syntheses=syntheses, multiple=True, datetime=datetime)
    
    pdf_file = None
    try:
        pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        HTML(string=html_content).write_pdf(pdf_file.name)
        return send_file(
            pdf_file.name,
            download_name=f'toutes_syntheses_archivees_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
            as_attachment=True
        )
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'error')
        return redirect(url_for('admin.archives'))
    finally:
        if pdf_file and os.path.exists(pdf_file.name):
            os.unlink(pdf_file.name)

@admin_bp.route('/archives/download-filtered')
@login_required
def download_all_archives_filtered():
    from utils import generate_pdf_synthesis
    import tempfile
    from weasyprint import HTML
    from flask import render_template
    from datetime import datetime, time
    
    # Get date filters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = Synthesis.query.filter_by(archived=True)
    
    # Apply date filters if provided
    if start_date:
        start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min)
        query = query.filter(Synthesis.archive_date >= start_datetime)
    if end_date:
        end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max)
        query = query.filter(Synthesis.archive_date <= end_datetime)
    
    # Get filtered syntheses
    syntheses = query.order_by(Synthesis.archive_date.desc()).all()
    
    if not syntheses:
        flash('Aucune synthèse archivée trouvée pour la période sélectionnée.', 'warning')
        return redirect(url_for('admin.archives'))
    
    # Generate combined PDF
    html_content = render_template('admin/pdf_synthesis.html', syntheses=syntheses, multiple=True, datetime=datetime)
    
    pdf_file = None
    try:
        pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        HTML(string=html_content).write_pdf(pdf_file.name)
        
        # Create filename with date range
        filename = 'syntheses_archivees'
        if start_date:
            filename += f'_depuis_{start_date}'
        if end_date:
            filename += f'_jusquau_{end_date}'
        filename += f'_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
        
        return send_file(
            pdf_file.name,
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'error')
        return redirect(url_for('admin.archives'))
    finally:
        if pdf_file and os.path.exists(pdf_file.name):
            os.unlink(pdf_file.name)



@admin_bp.route('/archive/<int:synthesis_id>/delete', methods=['POST'])
@login_required
def delete_archive(synthesis_id):
    try:
        synthesis = Synthesis.query.filter_by(id=synthesis_id, archived=True).first_or_404()
        db.session.delete(synthesis)
        db.session.commit()
        flash('Synthèse archivée supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la synthèse: {str(e)}', 'danger')
    
    return redirect(url_for('admin.archives'))

@admin_bp.route('/archives/delete-all', methods=['POST'])
@login_required
def delete_all_archives():
    try:
        # Supprimer toutes les synthèses archivées
        syntheses = Synthesis.query.filter_by(archived=True).all()
        if not syntheses:
            flash('Aucune synthèse archivée à supprimer.', 'info')
            return redirect(url_for('admin.archives'))
            
        for synthesis in syntheses:
            db.session.delete(synthesis)
        
        db.session.commit()
        flash('Toutes les synthèses archivées ont été supprimées avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression des synthèses: {str(e)}', 'danger')
    
    return redirect(url_for('admin.archives'))
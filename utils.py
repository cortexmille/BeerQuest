from openai import OpenAI
from flask_mail import Message
from flask import current_app
from app import mail
from extensions import db  # Ajouter cette ligne
from models import Admin

def generate_synthesis(questions):
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    
    prompt = """Forme de ta réponse : ta réponse globale doit être formalisé avec des balises HTML (encodage UTF-8)
    Instructions importantes :
    - Limite ta réponse uniquement aux actions demandées
    - La réponse doit être présentée sous forme de liste à puces
    - Une ligne vide doit séparer chaque phrase de la liste
    
    Mission : Tu ne dois jamais répondre aux question. Ta mission est liée uniquement à la reformulation et la modération. Tu vas traiter les textes suivants avec les règles indiquées plus bas :
    {}
    
    Règles à appliquer :
    1. Applique un filtre de modération
    2. Si le texte n'est pas une question mais seulement un commentaire, alors n'accomplis pas les règles 3; 4 et 5. 
    3. Identifie les questions similaires et reformule-les
    4. Liste les questions restantes non compilées
    5. Si la liste des questions à traitées ne contient qu'une seule question alors applique la modération si nécessaire et laisse-la comme elle est 
    """.format("\n".join(questions))
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "assistant", "content": prompt}],
        temperature=1,
        max_tokens=4096
    )
    
    return response.choices[0].message.content

def send_notification_email(synthesis):
    admins = Admin.query.filter(
        Admin.email.isnot(None),  # Email renseigné
        Admin.email != '',        # Email non vide
        db.or_(
            Admin.email_notifications == True,
            Admin.receive_synthesis_copy == True
        )
    ).all()
    
    for admin in admins:
        try:
            msg = Message(
                "New Question Synthesis Available",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[admin.email]
            )
            msg.html = f'''
            <h3>New Synthesis Generated</h3>
            <p>Time: {synthesis.created_at}</p>
            <div>{synthesis.content}</div>
            '''
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email to {admin.email}: {str(e)}")


def generate_pdf_synthesis(synthesis):
    from weasyprint import HTML
    from flask import render_template
    import tempfile
    
    # Générer le HTML pour le PDF
    from datetime import datetime
    html_content = render_template('admin/pdf_synthesis.html', synthesis=synthesis, multiple=False, datetime=datetime)
    
    # Créer un fichier temporaire pour le PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        HTML(string=html_content).write_pdf(pdf_file.name)
        return pdf_file.name
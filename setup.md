# Guide d'Installation et Configuration

## Prérequis

- Python 3.11 ou supérieur
- PostgreSQL
- Un compte Gmail pour l'envoi des notifications
- Une clé API OpenAI pour la synthèse des questions

## Installation

### 1. Cloner le projet

```bash
git clone [URL_DU_PROJET]
cd [NOM_DU_PROJET]
```

### 2. Installation des dépendances Python

Les dépendances nécessaires sont :
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

### 3. Configuration de l'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Flask
FLASK_SECRET_KEY=votre_clé_secrète

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nom_base

# OpenAI
OPENAI_API_KEY=votre_clé_api_openai

# Email
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_application
```

### 4. Configuration de la base de données

1. Créez une base de données PostgreSQL
2. Mettez à jour la variable `DATABASE_URL` dans le fichier `.env`
3. La structure de la base de données sera automatiquement créée au premier lancement

### 5. Configuration du serveur mail

1. Activez l'authentification à 2 facteurs sur votre compte Gmail
2. Générez un mot de passe d'application
3. Utilisez ce mot de passe dans la variable `MAIL_PASSWORD`

## Démarrage

1. Lancez l'application :
```bash
python main.py
```

2. Accédez à l'application :
- Interface publique : http://localhost:5000
- Interface admin : http://localhost:5000/admin

### Compte administrateur par défaut
- Username : admin
- Email : admin@example.com
- Mot de passe : admin123

Il est recommandé de changer ces identifiants après la première connexion.

## Fonctionnalités

### Synthèse automatique
- La synthèse des questions est effectuée toutes les 3 minutes
- Utilise l'API OpenAI pour l'analyse
- Les résultats sont accessibles dans le tableau de bord admin

### Notifications par email
- Envoyées automatiquement lors de nouvelles questions
- Configuration modifiable dans le panneau administrateur

### Export PDF
- Disponible dans le panneau administrateur
- Filtrage par période
- Inclut les questions originales et les synthèses

## Surveillance et maintenance

### Logs
- Les logs de l'application sont disponibles dans la console
- Les erreurs sont enregistrées avec horodatage

### Performances
- Monitoring temps réel dans le tableau de bord admin
- Statistiques d'utilisation disponibles

## Support

Pour toute question ou problème :
1. Vérifiez les logs d'erreur
2. Consultez la documentation technique
3. Contactez l'équipe de support

## Notes de sécurité

- Changez immédiatement le mot de passe administrateur par défaut
- Utilisez des mots de passe forts
- Gardez vos clés API confidentielles
- Mettez régulièrement à jour les dépendances

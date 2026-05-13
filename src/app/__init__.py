from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gizli-anahtar-buraya'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
    
    import os
    database_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL', 'sqlite:///veritabani.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    db.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    with app.app_context():
        from . import models 
        db.create_all()
        # Safe migration: add is_spoiler column if it doesn't exist
        try:
            import os
            if os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL', '').startswith('postgres'):
                db.session.execute(db.text("ALTER TABLE review ADD COLUMN IF NOT EXISTS is_spoiler BOOLEAN DEFAULT FALSE NOT NULL"))
            else:
                db.session.execute(db.text("ALTER TABLE review ADD COLUMN is_spoiler BOOLEAN DEFAULT 0 NOT NULL"))
            db.session.commit()
        except Exception:
            db.session.rollback()
            
        # Enforce Admin rights
        try:
            admin_names = ["arda", "arda burak", "kadir", "ömer", "omer", "alper", "burak", "halil"]
            all_users = models.User.query.all()
            for user in all_users:
                if user.username.lower() in admin_names:
                    user.is_admin = True
            db.session.commit()
        except Exception:
            db.session.rollback()

    return app

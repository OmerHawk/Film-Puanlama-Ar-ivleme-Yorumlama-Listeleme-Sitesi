from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gizli-anahtar-buraya'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
    
    db.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    with app.app_context():
        from . import models 
        db.create_all()      

    return app

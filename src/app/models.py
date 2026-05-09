from src.app import db
from datetime import datetime

watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) 
    is_admin = db.Column(db.Boolean, default=False, nullable=False) 
    
    # İlişkiler
    reviews = db.relationship('Review', backref='author', lazy=True)
    # İzleme listesi bağlantısı
    saved_movies = db.relationship('Movie', secondary=watchlist, lazy='subquery',
        backref=db.backref('saved_by', lazy=True))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster_url = db.Column(db.String(255), nullable=True)
    
    # İlişkiler
    reviews = db.relationship('Review', backref='movie', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=True) # made optional for comments without rating
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    replies = db.relationship('Reply', backref='review', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='review', lazy=True, cascade='all, delete-orphan')

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('replies', lazy=True, cascade='all, delete-orphan'))

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip = db.Column(db.Integer, nullable=False) # 1 for up, -1 for down
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('votes', lazy=True, cascade='all, delete-orphan'))
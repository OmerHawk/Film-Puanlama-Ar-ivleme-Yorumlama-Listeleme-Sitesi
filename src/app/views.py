from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1>Film Oneri Sitemize Hosgeldiniz! - Arda</h1>"

@views.route('/login')
def login():
    return "<h1>Burasi Giris Yapma Sayfasi Olacak</h1>"
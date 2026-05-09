import os
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, session

from werkzeug.security import generate_password_hash, check_password_hash
from src.app.crud import kullanici_getir_username, kullanici_getir_email, kullanici_olustur, tum_kullanicilari_getir
from src.api.tmdb_client import populer_filmleri_cek
from src.app.models import db, Review, Vote, Reply, User, Movie
from flask import jsonify

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if 'kullanici' in session:
        return redirect(url_for('views.dashboard'))
    return redirect(url_for('views.login'))

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        sifre = request.form.get('password')
        
        user = kullanici_getir_email(email)
        
        if user:
            db_sifre = getattr(user, 'password_hash', getattr(user, 'password', ''))
            
            if check_password_hash(db_sifre, sifre):
                session['kullanici'] = user.username
                session['email'] = user.email
                return redirect(url_for('views.dashboard'))
            else:
                return "<h1>Hata: Şifre yanlış! <a href='/login'>Geri Dön</a></h1>"
        else:
            return "<h1>Hata: Böyle bir e-posta bulunamadı! <a href='/login'>Geri Dön</a></h1>"
    
    return render_template("login.html")

@views.route('/dashboard')
def dashboard():
    if 'kullanici' in session:
        aktif_isim = session['kullanici']

        mevcut_klasor = os.path.dirname(os.path.abspath(__file__)) 
        src_klasoru = os.path.dirname(mevcut_klasor)               
        ana_dizin = os.path.dirname(src_klasoru)                   
        
        json_yolu_1 = os.path.join(ana_dizin, "data", "movies.json")
        json_yolu_2 = os.path.join(ana_dizin, "veri", "filmler.json")
        
        secilen_film = None
        
        try:
            if os.path.exists(json_yolu_1):
                with open(json_yolu_1, 'r', encoding='utf-8') as dosya:
                    json_filmler = json.load(dosya)
            elif os.path.exists(json_yolu_2):
                with open(json_yolu_2, 'r', encoding='utf-8') as dosya:
                    json_filmler = json.load(dosya)
            else:
                raise FileNotFoundError

            secilen_film = random.choice(json_filmler)
            
        except FileNotFoundError:
            secilen_film = {"film_adi": "Veritabanı Güncelleniyor...", "ozet": "Lütfen bekleyin.", "puan": "-"}

        try:
            populer_filmler = populer_filmleri_cek(1)
            user = kullanici_getir_email(session.get('email'))
            admin_yetkisi = user.is_admin if user else False
            return render_template("Dashboard.html", aktif_isim=aktif_isim, filmler=populer_filmler, rastgele_film=secilen_film, is_admin=admin_yetkisi)
            
        except Exception as e:
            return f"<h1>Hosgeldin {aktif_isim}!</h1><p>Filmler yuklenirken bir hata olustu: {e}</p><a href='/logout'>Cikis Yap</a>"
            
    else:
        return redirect(url_for('views.login'))

@views.route('/logout')
def logout():
    session.pop('kullanici', None)
    session.pop('email', None)
    return redirect(url_for('views.login'))

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        kullanici_adi = request.form.get('name') or request.form.get('username')
        email = request.form.get('email')
        sifre = request.form.get('password')
        
        if kullanici_getir_email(email):
            return "<h1>Hata: Bu e-posta adresi zaten kayıtlı! <a href='/register'>Geri Dön</a></h1>"
            
        if kullanici_getir_username(kullanici_adi):
            return "<h1>Hata: Bu kullanıcı adı zaten alınmış! <a href='/register'>Geri Dön</a></h1>"

        hashed_password = generate_password_hash(sifre, method='pbkdf2:sha256')
        
        proje_ekibi = ["arda", "kadir", "ömer", "omer", "alper", "burak", "halil"]
        kullanici_admin_mi = True if kullanici_adi.lower() in proje_ekibi else False

        yeni_user = kullanici_olustur(kullanici_adi, email, hashed_password, is_admin=kullanici_admin_mi)
        
        if yeni_user:
            return "<h1>Kayıt Başarılı! Şimdi <a href='/login'>Giriş Yapabilirsin</a>.</h1>"
        return "<h1>Kayıt sırasında bir hata oluştu!</h1>"

    return render_template("LoginScreen.html")

@views.route('/admin')
def admin_panel():
    user = kullanici_getir_email(session.get('email'))
    if user and user.is_admin:
        try:
            kullanicilar = tum_kullanicilari_getir()
        except:
            kullanicilar = [] 
            
        return render_template("Adminscreen.html", users=kullanicilar)
    else:
        return "<h1>Dur orda! Bu sayfaya girmek için yetkiniz yok. Sadece proje ekibi girebilir.</h1>", 403

@views.route('/film/<int:id>')
def film_detay(id):
    kullanici = session.get('kullanici', '')
    user_obj = kullanici_getir_username(kullanici) if kullanici else None
    is_admin = getattr(user_obj, 'is_admin', False) if user_obj else False
    return render_template("MovieDetails.html", film_id=id, current_user=kullanici, is_admin=is_admin)

@views.route('/api/filmler/<int:film_id>/yorumlar', methods=['GET', 'POST'])
def api_yorumlar(film_id):
    if request.method == 'GET':
        reviews = Review.query.filter_by(movie_id=film_id).order_by(Review.date_posted.desc()).all()
        yorumlar_data = []
        for r in reviews:
            replies = [{"id": rep.id, "userId": rep.user.username, "metin": rep.comment, "tarih": rep.date_posted} for rep in r.replies]
            upvotes = Vote.query.filter_by(review_id=r.id, tip=1).count()
            downvotes = Vote.query.filter_by(review_id=r.id, tip=-1).count()
            yorumlar_data.append({
                "id": r.id,
                "filmId": r.movie_id,
                "userId": r.author.username,
                "metin": r.comment,
                "tarih": r.date_posted,
                "begeniler": r.likes,
                "yanitlar": replies,
                "upvotes": upvotes,
                "downvotes": downvotes
            })
        return jsonify({"yorumlar": yorumlar_data})
        
    elif request.method == 'POST':
        if 'kullanici' not in session:
            return jsonify({"hata": "Giriş yapmalısınız"}), 401
        data = request.json
        metin = data.get("metin")
        user = kullanici_getir_username(session['kullanici'])
        if not metin:
            return jsonify({"hata": "Metin boş olamaz"}), 400
        
        yeni_yorum = Review(rating=None, comment=metin, user_id=user.id, movie_id=film_id)
        db.session.add(yeni_yorum)
        db.session.commit()
        
        return jsonify({
            "id": yeni_yorum.id,
            "filmId": film_id,
            "userId": user.username,
            "metin": metin,
            "tarih": yeni_yorum.date_posted,
            "begeniler": 0,
            "yanitlar": [],
            "upvotes": 0,
            "downvotes": 0
        }), 201

@views.route('/api/yorumlar/<int:yorum_id>', methods=['POST', 'PUT', 'DELETE'])
def api_yorum_islem(yorum_id):
    if 'kullanici' not in session:
        return jsonify({"hata": "Giriş yapmalısınız"}), 401
    
    user = kullanici_getir_username(session['kullanici'])
    action = request.args.get('action')
    yorum = Review.query.get_or_404(yorum_id)
    
    if request.method == 'DELETE':
        if yorum.user_id != user.id and not user.is_admin:
            return jsonify({"hata": "Yetkiniz yok"}), 403
        db.session.delete(yorum)
        db.session.commit()
        return jsonify({"mesaj": "Silindi"})
        
    if request.method == 'PUT':
        if yorum.user_id != user.id:
            return jsonify({"hata": "Yetkiniz yok"}), 403
        data = request.json
        yorum.comment = data.get("metin", yorum.comment)
        db.session.commit()
        return jsonify({"mesaj": "Güncellendi", "metin": yorum.comment})
        
    if request.method == 'POST':
        if action == 'begen':
            yorum.likes += 1
            db.session.commit()
            return jsonify({"beg": yorum.likes})
            
        elif action == 'vote':
            data = request.json
            tip = data.get("tip")
            existing_vote = Vote.query.filter_by(review_id=yorum.id, user_id=user.id).first()
            if existing_vote:
                existing_vote.tip = tip
            else:
                yeni_vote = Vote(tip=tip, user_id=user.id, review_id=yorum.id)
                db.session.add(yeni_vote)
            db.session.commit()
            upvotes = Vote.query.filter_by(review_id=yorum.id, tip=1).count()
            downvotes = Vote.query.filter_by(review_id=yorum.id, tip=-1).count()
            return jsonify({"upvotes": upvotes, "downvotes": downvotes})
            
        elif action == 'yanit':
            data = request.json
            metin = data.get("metin")
            yeni_yanit = Reply(comment=metin, user_id=user.id, review_id=yorum.id)
            db.session.add(yeni_yanit)
            db.session.commit()
            return jsonify({
                "id": yeni_yanit.id,
                "userId": user.username,
                "metin": yeni_yanit.comment,
                "tarih": yeni_yanit.date_posted
            })
    return jsonify({"hata": "Geçersiz işlem"}), 400

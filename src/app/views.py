import os
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.app.crud import (kullanici_getir_username, kullanici_getir_email, kullanici_olustur, 
                        tum_kullanicilari_getir, kullanici_sil, log_ekle, tum_loglari_getir)
from src.api.tmdb_client import populer_filmleri_cek, film_detay_cek, film_ara, ture_gore_filmleri_getir
from src.app.models import db, Review, Vote, Reply, User, Movie

views = Blueprint('views', __name__)

def dogrulama_maili_gonder(alici_mail, kod):
    gonderici_mail = "cinerate3@gmail.com"  
    sifre = "vgsjazzfojiplcpk" 
    
    mesaj = MIMEMultipart()
    mesaj['From'] = gonderici_mail
    mesaj['To'] = alici_mail
    mesaj['Subject'] = "Cinerate - Kayıt Onay Kodunuz"
    
    govde = f"Cinerate platformuna hoş geldiniz!\n\nKayıt işleminizi tamamlamak için 6 haneli onay kodunuz: {kod}\n\nBu kodu kimseyle paylaşmayın."
    mesaj.attach(MIMEText(govde, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gonderici_mail, sifre)
        server.send_message(mesaj)
        server.quit()
        return True
    except Exception as e:
        print("Mail hatası:", e)
        return False

@views.route('/')
def home():
    return redirect(url_for('views.dashboard'))

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
                log_ekle(user.username, "Sisteme giriş yaptı.")
                return redirect(url_for('views.dashboard'))
            else:
                return "<h1>Hata: Şifre yanlış! <a href='/login'>Geri Dön</a></h1>"
        else:
            return "<h1>Hata: Böyle bir e-posta bulunamadı! <a href='/login'>Geri Dön</a></h1>"
    return render_template("LoginScreen.html", kod_bekleniyor=False, login_mode=True)

@views.route('/dashboard')
def dashboard():
    user = kullanici_getir_email(session.get('email')) if 'email' in session else None
    aktif_isim = user.username if user else "Misafir"
    admin_yetkisi = user.is_admin if user else False
    is_logged_in = 'kullanici' in session
    
    try:
        populer_filmler = populer_filmleri_cek(2) # 40 film
        
        # Kategoriler (Action=28, Comedy=35, Horror=27, Sci-Fi=878, Romance=10749, Animation=16)
        kategoriler = [
            {"isim": "Aksiyon", "icon": "local_fire_department", "filmler": ture_gore_filmleri_getir(28)},
            {"isim": "Komedi", "icon": "sentiment_very_satisfied", "filmler": ture_gore_filmleri_getir(35)},
            {"isim": "Korku", "icon": "skull", "filmler": ture_gore_filmleri_getir(27)},
            {"isim": "Bilim Kurgu", "icon": "rocket_launch", "filmler": ture_gore_filmleri_getir(878)},
            {"isim": "Romantik", "icon": "favorite", "filmler": ture_gore_filmleri_getir(10749)},
            {"isim": "Animasyon", "icon": "animation", "filmler": ture_gore_filmleri_getir(16)},
        ]
        
        return render_template("Dashboard.html", 
                             aktif_isim=aktif_isim, 
                             filmler=populer_filmler, 
                             kategoriler=kategoriler,
                             is_admin=admin_yetkisi,
                             current_user=user,
                             is_logged_in=is_logged_in)
    except Exception as e:
        return f"<h1>Sistemsel bir hata olustu: {e}</h1>"

@views.route('/logout')
def logout():
    session.pop('kullanici', None)
    session.pop('email', None)
    return redirect(url_for('views.login'))

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'otp_kodu' in request.form:
            girilen_kod = request.form.get('otp_kodu')
            gercek_kod = session.get('onay_kodu')
            
            if str(girilen_kod) == str(gercek_kod):
                kullanici_adi = session.get('gecici_isim')
                email = session.get('gecici_email')
                sifre = session.get('gecici_sifre')
                
                hashed_password = generate_password_hash(sifre, method='pbkdf2:sha256')
                proje_ekibi = ["arda", "kadir", "ömer", "omer", "alper", "burak", "halil"]
                kullanici_admin_mi = True if kullanici_adi.lower() in proje_ekibi else False

                yeni_user = kullanici_olustur(kullanici_adi, email, hashed_password, is_admin=kullanici_admin_mi)
                
                if yeni_user:
                    log_ekle(kullanici_adi, "Sisteme yeni üye olarak kayıt oldu ve e-postasını doğruladı.")
                    session.pop('onay_kodu', None)
                    session.pop('gecici_isim', None)
                    session.pop('gecici_email', None)
                    session.pop('gecici_sifre', None)
                    return "<h1>Kayıt Başarılı! Şimdi <a href='/login'>Giriş Yapabilirsin</a>.</h1>"
            else:
                return "<h1>Hata: Kod yanlış! <a href='/register'>Baştan Dene</a></h1>"
        else:
            kullanici_adi = request.form.get('name') or request.form.get('username')
            email = request.form.get('email')
            sifre = request.form.get('password')
            
            if kullanici_getir_email(email):
                return "<h1>Hata: Bu e-posta adresi zaten kayıtlı! <a href='/register'>Geri Dön</a></h1>"
            if kullanici_getir_username(kullanici_adi):
                return "<h1>Hata: Bu kullanıcı adı zaten alınmış! <a href='/register'>Geri Dön</a></h1>"

            onay_kodu = str(random.randint(100000, 999999))
            session['onay_kodu'] = onay_kodu
            session['gecici_isim'] = kullanici_adi
            session['gecici_email'] = email
            session['gecici_sifre'] = sifre
                
            dogrulama_maili_gonder(email, onay_kodu)
            return render_template("LoginScreen.html", kod_bekleniyor=True, gizli_email=email)

    return render_template("LoginScreen.html", kod_bekleniyor=False)

@views.route('/admin')
def admin_panel():
    user = kullanici_getir_email(session.get('email'))
    if user and user.is_admin:
        try:
            kullanicilar = tum_kullanicilari_getir()
            loglar = tum_loglari_getir() 
        except:
            kullanicilar = [] 
            loglar = [] 
        return render_template("Adminscreen.html", users=kullanicilar, logs=loglar)
    else:
        return "<h1>Dur orda! Yetkiniz yok.</h1>", 403

@views.route('/film/<int:id>')
def film_detay(id):
    kullanici = session.get('kullanici', '')
    user_obj = kullanici_getir_username(kullanici) if kullanici else None
    is_admin = getattr(user_obj, 'is_admin', False) if user_obj else False
    
    film_data = film_detay_cek(id)
    if not film_data:
        film_data = {
            "id": id,
            "film_adi": "Bilinmeyen Film",
            "ozet": "Film bilgisi bulunamadı.",
            "afis_yolu": None,
            "arka_plan": None,
            "puan": 0.0,
            "sure": 0,
            "turler": []
        }
        
    cinerate_avg = db.session.query(func.avg(Review.rating)).filter(Review.movie_id == id, Review.rating.isnot(None)).scalar()
    cinerate_puan = round(cinerate_avg, 1) if cinerate_avg is not None else 0.0
        
    return render_template("MovieDetails.html", 
                           film_id=id, 
                           film=film_data,
                           cinerate_puan=cinerate_puan,
                           current_user=user_obj, 
                           is_admin=is_admin)

@views.route('/api/filmler/<int:film_id>/yorumlar', methods=['GET', 'POST'])
def api_yorumlar(film_id):
    if request.method == 'GET':
        try:
            reviews = Review.query.filter_by(movie_id=film_id).order_by(Review.date_posted.desc()).all()
            yorumlar_data = []
            for r in reviews:
                replies = [{"id": rep.id, "userId": rep.user.username, "metin": rep.comment, "tarih": str(rep.date_posted)} for rep in r.replies]
                upvotes = Vote.query.filter_by(review_id=r.id, tip=1).count()
                downvotes = Vote.query.filter_by(review_id=r.id, tip=-1).count()
                yorumlar_data.append({
                    "id": r.id,
                    "filmId": r.movie_id,
                    "userId": r.author.username,
                    "metin": r.comment,
                    "tarih": str(r.date_posted),
                    "begeniler": r.likes,
                    "yanitlar": replies,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "rating": r.rating
                })
            return jsonify({"yorumlar": yorumlar_data})
        except Exception as e:
            return jsonify({"hata": str(e), "yorumlar": []}), 500
        
    elif request.method == 'POST':
        if 'kullanici' not in session:
            return jsonify({"hata": "Giriş yapmalısınız"}), 401
        data = request.json
        metin = data.get("metin")
        puan = data.get("rating")
        user = kullanici_getir_username(session['kullanici'])
        if not user:
            session.clear()
            return jsonify({"hata": "Oturumunuz geçersiz, lütfen tekrar giriş yapın."}), 401
            
        if not metin:
            return jsonify({"hata": "Metin boş olamaz"}), 400
        
        movie = Movie.query.get(film_id)
        if not movie:
            film_data = film_detay_cek(film_id)
            if film_data:
                yil = 2000
                turler = film_data.get('turler', [])
                if isinstance(turler, list):
                    turler = ', '.join(turler) if turler else 'Bilinmeyen'
                movie = Movie(
                    id=film_id,
                    tmdb_id=film_id,
                    title=film_data.get('film_adi', 'Bilinmeyen'),
                    year=yil,
                    genre=turler,
                    description=film_data.get('ozet', ''),
                    poster_url=film_data.get('afis_yolu')
                )
                db.session.add(movie)
                db.session.commit()

        yeni_yorum = Review(rating=puan, comment=metin, user_id=user.id, movie_id=film_id)
        db.session.add(yeni_yorum)
        db.session.commit()
        
        return jsonify({
            "id": yeni_yorum.id,
            "filmId": film_id,
            "userId": user.username,
            "metin": metin,
            "tarih": str(yeni_yorum.date_posted),
            "begeniler": 0,
            "yanitlar": [],
            "upvotes": 0,
            "downvotes": 0,
            "rating": puan
        }), 201

@views.route('/api/yorumlar/<int:yorum_id>', methods=['POST', 'PUT', 'DELETE'])
def api_yorum_islem(yorum_id):
    if 'kullanici' not in session:
        return jsonify({"hata": "Giriş yapmalısınız"}), 401
    
    user = kullanici_getir_username(session['kullanici'])
    if not user:
        session.clear()
        return jsonify({"hata": "Oturumunuz geçersiz, lütfen tekrar giriş yapın."}), 401
        
    action = request.args.get('action')
    yorum = Review.query.get(yorum_id)
    if not yorum:
        return jsonify({"hata": "Yorum bulunamadı"}), 404
    
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

@views.route('/kullanici-sil/<int:id>', methods=['POST'])
def kullaniciyi_sil(id):
    user = kullanici_getir_email(session.get('email'))
    if user and user.is_admin:
        log_ekle(user.username, f"Sistemden bir kullanıcıyı (ID: {id}) sildi.")
        kullanici_sil(id)
        return redirect(url_for('views.admin_panel'))
    else:
        return "<h1>Dur orda! Yetkiniz yok.</h1>", 403
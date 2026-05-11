import os
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, session

from werkzeug.security import generate_password_hash, check_password_hash
from src.app.crud import kullanici_getir_username, kullanici_getir_email, kullanici_olustur, tum_kullanicilari_getir, kullanici_sil, log_ekle, tum_loglari_getir
from src.api.tmdb_client import populer_filmleri_cek

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
                log_ekle(user.username, "Sisteme giriş yaptı.")
                return redirect(url_for('views.dashboard'))
            else:
                return "<h1>Hata: Şifre yanlış! <a href='/login'>Geri Dön</a></h1>"
        else:
            return "<h1>Hata: Böyle bir e-posta bulunamadı! <a href='/login'>Geri Dön</a></h1>"
    
    return render_template("login.html")

@views.route('/dashboard')
def dashboard():
    if 'kullanici' in session:
        try:
            # API'den güncel popüler filmleri çekiyoruz
            populer_filmler = populer_filmleri_cek(1) 
            
            # Veritabanından giriş yapan kullanıcının bilgilerini alıyoruz
            user = kullanici_getir_email(session.get('email'))
            aktif_isim = user.username if user else session['kullanici']
            admin_yetkisi = user.is_admin if user else False
            
            # Verileri Dashboard.html tasarımına gönderiyoruz
            return render_template("Dashboard.html", 
                                 aktif_isim=aktif_isim, 
                                 filmler=populer_filmler, 
                                 is_admin=admin_yetkisi)
            
        except Exception as e:
            return f"<h1>Sistemsel bir hata olustu: {e}</h1>"
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
                    # Hafızayı temizle
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
    return render_template("MovieDetails.html", film_id=id)

@views.route('/kullanici-sil/<int:id>', methods=['POST'])
def kullaniciyi_sil(id):
    user = kullanici_getir_email(session.get('email'))
    if user and user.is_admin:
        log_ekle(user.username, f"Sistemden bir kullanıcıyı (ID: {id}) sildi.")
        
        kullanici_sil(id)
        return redirect(url_for('views.admin_panel'))
    else:
        return "<h1>Dur orda! Yetkiniz yok.</h1>", 403
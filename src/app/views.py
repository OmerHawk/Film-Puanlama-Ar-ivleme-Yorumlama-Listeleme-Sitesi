import os
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, session
from src.api.tmdb_client import filmleri_getir, veriyi_ayikla

views = Blueprint('views', __name__)

# 1. ANA SAYFA KONTROLÜ
@views.route('/')
def home():
    # Eğer kullanıcının bilekliği varsa direkt içeri (dashboard) al
    if 'kullanici' in session:
        return redirect(url_for('views.dashboard'))
    # Bilekliği yoksa kapıya (login) yönlendir
    return redirect(url_for('views.login'))

# 2. GİRİŞ YAP SAYFASI
@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici_adi = request.form.get('username')
        sifre = request.form.get('password')
        
        # İleride burada Burak'ın veritabanına "Bu şifre doğru mu?" diye soracağız.
        # Şimdilik herkesi doğru kabul edip bilekliği takıyoruz:
        session['kullanici'] = kullanici_adi
        
        # Giriş başarılı, onu direkt içerideki sayfaya fırlat:
        return redirect(url_for('views.dashboard'))
    
    return render_template("login.html")

# 3. YENİ: İÇERİDEKİ ÖZEL SAYFA (DASHBOARD)
@views.route('/dashboard')
def dashboard():
    # Güvenlik Kontrolü: Bu adamın bilekliği var mı?
    if 'kullanici' in session:
        aktif_isim = session['kullanici']

        mevcut_klasor = os.path.dirname(os.path.abspath(__file__)) 
        src_klasoru = os.path.dirname(mevcut_klasor)               
        ana_dizin = os.path.dirname(src_klasoru)                   
        
        json_yolu_1 = os.path.join(ana_dizin, "data", "movies.json")
        json_yolu_2 = os.path.join(ana_dizin, "veri", "filmler.json")
        
        rastgele_film_html = ""
        
        try:
            if os.path.exists(json_yolu_1):
                with open(json_yolu_1, 'r', encoding='utf-8') as dosya:
                    filmler = json.load(dosya)
            elif os.path.exists(json_yolu_2):
                with open(json_yolu_2, 'r', encoding='utf-8') as dosya:
                    filmler = json.load(dosya)
            else:
                raise FileNotFoundError

            secilen_film = random.choice(filmler)
            
            film_adi = secilen_film.get("title", secilen_film.get("film_adi", "Bilinmeyen Film"))
            ozet = secilen_film.get("overview", secilen_film.get("ozet", "Özet yok."))
            puan = secilen_film.get("rating", secilen_film.get("puan", "-"))
            
            rastgele_film_html = f"""
            <div style='background-color: #f8f9fa; border-left: 5px solid #e50914; padding: 15px; margin-bottom: 20px;'>
                <h3 style='margin-top: 0; color: #e50914;'>🎲 Günün Rastgele Filmi</h3>
                <p><b>{film_adi}</b> (⭐ TMDB Puanı: {puan})</p>
                <p><i>{ozet}</i></p>
            </div>
            """
        except FileNotFoundError:
            rastgele_film_html = "<p><i>Rastgele film veritabanı şu an güncelleniyor...</i></p>"

        
        try:
            # 1. Arkadaşının API koduyla 1. sayfa popüler filmleri çekiyoruz
            ham_veri = filmleri_getir(1)
            
            # 2. Gelen karmaşık veriyi yine arkadaşının koduyla temizliyoruz
            filmler = veriyi_ayikla(ham_veri["results"])
            
            # 3. Ekrana basılacak basit HTML iskeletini oluşturuyoruz
            html_cikti = f"<h1>Hosgeldin {aktif_isim}! Iste TMDB Populer Filmler:</h1>"
            html_cikti += "<a href='/logout'>Cikis Yap</a><hr>"
            
         
            html_cikti += rastgele_film_html
            html_cikti += "<h2>🔥 TMDB Populer Filmler:</h2><ul>"
            
            
            # 4. Gelen temiz filmleri tek tek listeye (<li>) ekliyoruz
            for film in filmler:
                html_cikti += f"<li><b>{film['film_adi']}</b> - TMDB Puanı: {film['puan']}</li>"
                
            html_cikti += "</ul>"
            
            return html_cikti
            
        except Exception as e:
            # Eğer internet yoksa veya API bozuksa site çökmesin, hata mesajı versin
            return f"<h1>Hosgeldin {aktif_isim}!</h1><p>Filmler yuklenirken bir hata olustu: {e}</p><a href='/logout'>Cikis Yap</a>"
            
    else:
        # Bilekliği yoksa login'e kışla
        return redirect(url_for('views.login'))

# 4. YENİ: ÇIKIŞ YAPMA (LOGOUT)
@views.route('/logout')
def logout():
    # session.pop ile bilekliği çöpe atıyoruz
    session.pop('kullanici', None)
    return redirect(url_for('views.login'))

# 5. KAYIT OL SAYFASI (Eski haliyle kalabilir)
@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        kullanici_adi = request.form.get('username')
        sifre = request.form.get('password')
        return f"<h1>KAYIT BASARILI -> Kullanici: {kullanici_adi}, Sifre: {sifre}</h1>"
    return render_template("register.html")

@views.route('/film/<int:id>')
def film_detay(id):
    return f"<h1>Burasi {id} numarali filmin sayfasi. Detaylar gelecek.</h1>"

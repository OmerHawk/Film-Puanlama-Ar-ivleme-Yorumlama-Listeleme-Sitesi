from src.app import db
from src.app.models import User, Movie, Review

# KULLANICI (USER) İŞLEMLERİ

def kullanici_olustur(username, email, password_hash, is_admin=False):
    """Yeni bir kullanıcı oluşturur ve veritabanına kaydeder."""
    yeni_kullanici = User(
        username=username, 
        email=email, 
        password_hash=password_hash, 
        is_admin=is_admin
    )
    db.session.add(yeni_kullanici)
    db.session.commit()
    return yeni_kullanici

def kullanici_getir_username(username):
    """Kullanıcı adına göre kullanıcıyı bulur (Login ve yetki kontrolü için)."""
    return User.query.filter_by(username=username).first()

def kullanici_getir_email(email):
    """E-posta adresine göre kullanıcıyı bulur (Kayıt olurken 'Bu mail var mı?' kontrolü için)."""
    return User.query.filter_by(email=email).first()

# FİLM (MOVIE) İŞLEMLERİ 

def film_getir_veya_olustur(tmdb_id, title, year, genre="Belirtilmedi", description="Özet TMDB'den anlık çekilecek", poster_url=""):
    """
    Kullanıcı bir filme yorum yaptığında veya listesine eklediğinde çalışır.
    Film bizim veritabanımızda zaten varsa onu getirir, yoksa hibrit depolamaya
    uygun şekilde sadece temel bilgileriyle bir iskelet oluşturur.
    """
    film = Movie.query.filter_by(tmdb_id=tmdb_id).first()
    
    if not film:
        film = Movie(
            tmdb_id=tmdb_id,
            title=title,
            year=year,
            genre=genre,
            description=description, # Veritabanı şişmesin diye kısa tutuyoruz
            poster_url=poster_url
        )
        db.session.add(film)
        db.session.commit()
        
    return film


# YORUM VE PUAN (REVIEW) İŞLEMLERİ 

def filme_yorum_yap(user_id, movie_id, rating, comment):
    """Bir filme yeni bir yorum ve puan ekler (Float puanları destekler)."""
    yeni_yorum = Review(
        user_id=user_id,
        movie_id=movie_id,
        rating=float(rating), # Puanın ondalıklı gelmesini garanti altına alıyoruz
        comment=comment
    )
    db.session.add(yeni_yorum)
    db.session.commit()
    return yeni_yorum

def film_yorumlari_getir(movie_id):
    """Belirli bir filme yapılmış tüm yorumları liste halinde getirir."""
    return Review.query.filter_by(movie_id=movie_id).order_by(Review.date_posted.desc()).all()


# İZLEME LİSTESİ (WATCHLIST) İŞLEMLERİ 

def izleme_listesine_ekle(user_id, movie_id):
    """Bir filmi kullanıcının izleme listesine ekler."""
    kullanici = User.query.get(user_id)
    film = Movie.query.get(movie_id)
    
    if film and kullanici and (film not in kullanici.saved_movies):
        kullanici.saved_movies.append(film)
        db.session.commit()
        return True # Başarıyla eklendi
    return False # Film zaten listede veya bulunamadı

def izleme_listesinden_cikar(user_id, movie_id):
    """Bir filmi kullanıcının izleme listesinden çıkarır."""
    kullanici = User.query.get(user_id)
    film = Movie.query.get(movie_id)
    
    if film in kullanici.saved_movies:
        kullanici.saved_movies.remove(film)
        db.session.commit()
        return True
    return False
def tum_kullanicilari_getir():
    """Veritabanındaki tüm kullanıcıları liste halinde getirir."""
    return User.query.all()

# ==========================================
# ADMİN İŞLEMLERİ
# ==========================================

def kullanici_sil(user_id):
    """
    Belirtilen ID'ye sahip kullanıcıyı ve o kullanıcının 
    yaptığı tüm yorumları/izleme listesini veritabanından güvenle siler.
    """
    kullanici = User.query.get(user_id)
    
    if kullanici:
        # 1. Önce kullanıcının yaptığı tüm yorumları siliyoruz (Foreign Key hatası almamak için)
        for yorum in kullanici.reviews:
            db.session.delete(yorum)
            
        # 2. İzleme listesi bağlarını koparıyoruz
        kullanici.saved_movies = []
        
        # 3. Son olarak kullanıcının kendisini veritabanından siliyoruz
        db.session.delete(kullanici)
        db.session.commit()
        return True # Silme başarılı
        
    return False # Kullanıcı bulunamadı

from flask import Blueprint, render_template, request, redirect, url_for

views = Blueprint('views', __name__)

# 1. ANA SAYFA (Artık direkt Login'e yönlendiriyor)
@views.route('/')
def home():
    # url_for('views.login') -> "views içindeki login fonksiyonunun adresini (URL'sini) bul" demek
    # redirect(...) -> "Kullanıcıyı o adrese anında fırlat" demek
    return redirect(url_for('views.login'))

# methods=['GET', 'POST'] diyerek hem sayfayı açmayı hem de butona basmayı kabul ediyoruz
@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Butona basıldığında formdaki (name="..." olan) bilgileri çekiyoruz
        kullanici_adi = request.form.get('username')
        sifre = request.form.get('password')
        
        # Şimdilik Burak veritabanını kurmadığı için veriyi sadece ekrana yazdıralım
        return f"<h1>Gelen Bilgiler -> Kullanici: {kullanici_adi}, Sifre: {sifre}</h1>"
    
    # Eğer butona basılmadıysa (sadece sayfa açıldıysa) formu göster
    return render_template("login.html")

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
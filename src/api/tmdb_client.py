import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_anahtari = os.getenv("TMDB_API_KEY")
temel_adres = "https://api.themoviedb.org/3"

os.makedirs("veri", exist_ok=True)

def filmleri_getir(sayfa_no=1):
    adres = f"{temel_adres}/movie/popular"
    
    parametreler = {
        "api_key": api_anahtari,
        "language": "tr-TR",
        "page": sayfa_no
    }
    
    cevap = requests.get(adres, params=parametreler)
    cevap.raise_for_status()
    
    return cevap.json()

def tum_filmleri_topla(maks_sayfa=5):
    toplam_liste = []
    
    for sayfa in range(1, maks_sayfa + 1):
        print(f"{sayfa}. sayfa çekiliyor...")
        
        gelen_veri = filmleri_getir(sayfa)
        toplam_liste.extend(gelen_veri["results"])
        
    return toplam_liste

def veriyi_ayikla(ham_filmler):
    temiz_liste = []
    
    for film in ham_filmler:
        afis = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}" if film.get("poster_path") else None
        
        temiz_liste.append({
            "film_adi": film.get("title"),
            "ozet": film.get("overview"),
            "afis_yolu": afis,
            "puan": film.get("vote_average")
        })
        
    return temiz_liste

def dosyaya_yaz(veri, dosya_adi="veri/filmler.json"):
    with open(dosya_adi, "w", encoding="utf-8") as dosya:
        json.dump(veri, dosya, ensure_ascii=False, indent=2)
        
    print(f"Kayıt tamamlandı -> {dosya_adi}")

def calistir():
    try:
        print("İşlem başlıyor...")
        
        ham_veri = tum_filmleri_topla(5)
        son_veri = veriyi_ayikla(ham_veri)
        dosyaya_yaz(son_veri)
        
        print(f"Toplam alınan film sayısı: {len(son_veri)}")
        
    except requests.exceptions.RequestException as hata:
        print("Bağlantı sorunu:", hata)
        
    except Exception as hata:
        print("Beklenmeyen hata:", hata)

if __name__ == "__main__":
    calistir()

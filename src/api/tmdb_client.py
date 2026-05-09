import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_ANAHTARI = os.getenv("TMDB_API_KEY")
TEMEL_ADRES = "https://api.themoviedb.org/3"

if not API_ANAHTARI:
    raise ValueError("KRİTİK HATA: .env dosyası bulunamadı veya şifre okunamadı!")

def _sayfa_getir(sayfa_no=1):
    adres = f"{TEMEL_ADRES}/movie/popular"
    parametreler = {
        "api_key": API_ANAHTARI,
        "language": "tr-TR",
        "page": sayfa_no
    }
    
    cevap = requests.get(adres, params=parametreler)
    cevap.raise_for_status()
    
    return cevap.json().get("results", [])

def _veriyi_ayikla(ham_filmler):
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


def populer_filmleri_cek(sayfa_sayisi=1):
    tum_filmler = []
    
    try:
        for sayfa in range(1, sayfa_sayisi + 1):
            ham_veri = _sayfa_getir(sayfa)
            tum_filmler.extend(ham_veri)
            
        return _veriyi_ayikla(tum_filmler)
        
    except requests.exceptions.RequestException as hata:
        print(f"Bağlantı Hatası: {hata}")
        return [] 

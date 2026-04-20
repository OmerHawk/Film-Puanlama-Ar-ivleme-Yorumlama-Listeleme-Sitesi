# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import requests
from dotenv import load_dotenv
import json

# .env dosyasını yükle
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Data klasörü
os.makedirs("data", exist_ok=True)


def get_movies(page=1):
    """TMDB'den populer filmleri ceker"""
    url = f"{BASE_URL}/movie/popular"

    params = {
        "api_key": API_KEY,
        "language": "tr-TR",
        "page": page
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def fetch_all_movies(max_pages=5):
    """Birden fazla sayfa cekip tek liste yapar"""
    all_movies = []

    for page in range(1, max_pages + 1):
        print(f"{page}. sayfa çekiliyor...")

        data = get_movies(page)

        all_movies.extend(data["results"])

    return all_movies


def clean_movies(movies):
    """Veriyi temizler kullanılabilir hale getirir"""
    cleaned = []

    for m in movies:
        cleaned.append({
            "title": m.get("title"),
            "overview": m.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get("poster_path") else None,
            "rating": m.get("vote_average")
        })

    return cleaned


def save_to_json(data, filename="data/movies.json"):
    """JSON dosyasini kaydeder"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Veri kaydedildi → {filename}")


def main():
    try:
        print("Veri çekiliyor...")

        movies = fetch_all_movies(max_pages=5)
        cleaned = clean_movies(movies)
        save_to_json(cleaned)

        print(f"Toplam film: {len(cleaned)}")

    except requests.exceptions.RequestException as e:
        print("API hatası:", e)

    except Exception as e:
        print("Genel hata:", e)


if __name__ == "__main__":
    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

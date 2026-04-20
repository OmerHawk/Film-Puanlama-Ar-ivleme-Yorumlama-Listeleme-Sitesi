import json
import os

from src.api.tmdb_client import TMDBClient  # senin client dosyan

class MovieFetcher:
    def __init__(self):
        self.client = TMDBClient()
        os.makedirs("data", exist_ok=True)

    def clean_movie(self, movie):
        """Ham veriyi temizler"""
        return {
            "id": movie.get("id"),
            "title": movie.get("title"),
            "overview": movie.get("overview"),
            "rating": movie.get("vote_average"),
            "release_date": movie.get("release_date"),
            "poster": self.build_poster_url(movie.get("poster_path"))
        }

    def build_poster_url(self, path):
        if not path:
            return None
        return f"https://image.tmdb.org/t/p/w500{path}"

    def fetch_all(self, pages=5):
        """Birden fazla sayfa veri çeker"""
        all_movies = []

        for page in range(1, pages + 1):
            print(f"{page}. sayfa çekiliyor...")

            data = self.client.get_popular_movies(page=page)

            for movie in data.get("results", []):
                all_movies.append(self.clean_movie(movie))

        return all_movies

    def save(self, movies, filename="data/movies.json"):
        """JSON'a kaydeder"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)

        print(f"{len(movies)} film kaydedildi → {filename}")


def main():
    fetcher = MovieFetcher()

    movies = fetcher.fetch_all(pages=5)  # ~100 film
    fetcher.save(movies)

    print("Bitti!")


if __name__ == "__main__":
    main()

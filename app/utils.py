TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def get_poster_url(tmdb_id):
    if tmdb_id:
        return f"{TMDB_IMAGE_BASE}/{tmdb_id}.jpg"
    return None


def extract_genres(movies_df):
    genres_set = set()

    for genres in movies_df["genres"]:
        for g in genres.split("|"):
            genres_set.add(g)

    return sorted(genres_set)

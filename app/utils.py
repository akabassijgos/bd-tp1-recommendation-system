
def extract_genres(movies_df):
    genres_set = set()

    for genres in movies_df["genres"]:
        for g in genres.split("|"):
            genres_set.add(g)

    return sorted(genres_set)

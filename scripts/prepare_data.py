import pandas as pd

# Load data
movies = pd.read_csv("data/ml-latest-small/movies.csv")
ratings = pd.read_csv("data/ml-latest-small/ratings.csv")
links = pd.read_csv("data/ml-latest-small/links.csv")

# Merge movies with TMDb IDs
movies = movies.merge(links, on="movieId", how="left")

# Clean TMDb IDs (some are missing)
movies = movies.dropna(subset=["tmdbId"])
movies["tmdbId"] = movies["tmdbId"].astype(int)

# Extract year from title
movies["year"] = movies["title"].str.extract(r"\((\d{4})\)")
movies["year"] = pd.to_numeric(movies["year"], errors="coerce")

# Remove year from title
movies["title"] = movies["title"].str.replace(r"\s*\(\d{4}\)", "", regex=True)

# Keep useful columns
movies_clean = movies[[
    "movieId",
    "title",
    "genres",
    "year",
    "tmdbId"
]]

# Save cleaned version
movies_clean.to_csv("data/movies_clean.csv", index=False)
ratings.to_csv("data/ratings_clean.csv", index=False)

print("Data prepared successfully.")
print(movies_clean.head())

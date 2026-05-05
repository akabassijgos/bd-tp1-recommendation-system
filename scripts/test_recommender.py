from app.recommender import *

ratings, movies = load_data()
matrix, user_map, movie_map = build_sparse_matrix(ratings)
sim = compute_item_similarity(matrix)

user_id = ratings["user_id"].iloc[0]

recs = recommend_items(user_id, ratings, matrix, user_map, movie_map, sim)

print(recs[:10])

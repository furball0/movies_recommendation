import pandas as pd
import sqlite3

conn = sqlite3.connect('recommendation.db')
cursor = conn.cursor()


def is_db_exist():
    cursor.execute("""
    select name from sqlite_master 
    where type='table' and name='recommendation_movies'
    """)
    table_exists = cursor.fetchall()
    if table_exists:
        return True
    return False


def init_db():
    if not is_db_exist():
        movies_info = pd.read_csv('data/new_movies_overview.csv', encoding='cp1252')
        recommendation_movies = pd.read_csv('data/recommendation_coefficient.csv')

        movies_info.to_sql('movies_overview', conn, if_exists='replace', index=False)
        recommendation_movies.to_sql('recommendation_movies', conn, if_exists='replace', index=False)
        cursor.executescript("""
        create table user_info(
            user_id integer,
            movie_imdb_id text,
            user_vote_rating integer,
            att_timestamp datetime default current_timestamp
        )
        """)
        return 1
    return 0

import sqlite3
from typing import List
import create_db

create_db.init_db()

conn = sqlite3.connect('recommendation.db', check_same_thread=False)
cursor = conn.cursor()


def get_cursor():
    return cursor


def fetchall(table: str, columns: List[str]):
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table} limit 10")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def movie_info(imdb_id: str):
    sql = f"""
        select 
            t.imdb_id,
            t.title,
            t.genres,
            t.overview,
            t.production_countries,
            t.movie_duration,
            t.year,
            t.vote_average,
            t.production_companies
        from movies_overview t
        where t.imdb_id = "{imdb_id}"
        """
    cursor.execute(sql)
    row = cursor.fetchall()[0]
    result = {'imdb_id': row[0], 'movie_title': row[1], 'genres': row[2], 'overview': row[3],
              'production_countries': row[4], 'movie_duration': row[5], 'release_year': row[6],
              'vote_average': row[7], 'production_companies': row[8]}
    return result


def get_imdb_id(movie_title: str, movie_year: int) -> str:
    sql = f"""
    select imdb_id from movies_overview mo
    where (mo.original_title = "{movie_title}" or mo.title = "{movie_title}") and mo.year = {movie_year}
    """
    cursor.execute(sql)
    imdb_id = cursor.fetchall()[0][0]
    return imdb_id


def insert_new_movie(user_id: int, movie_imdb_id: str, user_vote_rating: int):
    if user_vote_rating > 10:
        user_vote_rating = 10
    if user_vote_rating < 0:
        user_vote_rating = 0
    sql = f"""
        select *
        from user_info t
        where t.user_id = {user_id} and t.movie_imdb_id = '{movie_imdb_id}'
        """
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0:
        cursor.execute(f"""
        insert into user_info (user_id, movie_imdb_id, user_vote_rating) 
        values ({user_id}, '{movie_imdb_id}', {user_vote_rating})
        """)
    else:
        cursor.execute(f"""
        delete from user_info where user_id = {user_id} and movie_imdb_id = '{movie_imdb_id}';
        """)
        cursor.execute(f"""
        insert into user_info (user_id, movie_imdb_id, user_vote_rating)
                        values ({user_id},'{movie_imdb_id}', {user_vote_rating})
        """)
    conn.commit()


def delete_viewed_movie(user_id: int, movie_imdb_id: str):
    sql = f"""
        select *
        from user_info t
        where t.user_id = {user_id} and t.movie_imdb_id = '{movie_imdb_id}'
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) != 0:
        cursor.execute(f"""
        delete from user_info where user_id = {user_id} and movie_imdb_id = '{movie_imdb_id}';
        """)
        conn.commit()
        return True
    else:
        return False


def get_user_history(user_id):
    sql = f"""
        select 
            t.user_id,
            t.movie_imdb_id,
            t.user_vote_rating,
            t.att_timestamp
        from user_info t
        where t.user_id = {user_id}
        order by 4 desc
        """
    cursor.execute(sql)
    rows = cursor.fetchall()
    result = [{'user_id': row[0],
               'movie_title': str(movie_info(row[1])["movie_title"]),
               'release_year': int(movie_info(row[1])["release_year"]),
               'user_vote_rating': row[2],
               'datetime': row[3]} for row in rows]
    return result

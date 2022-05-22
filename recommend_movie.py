from typing import List, NamedTuple, Optional
import database_module as db

class Viewed_Movie(NamedTuple):
    """Структура просмотренного фильма пользователем"""
    user_id: int
    viewed_movie_id: int
    user_vote_rating: int

class Recommend_Movie(NamedTuple):
    movie_title: str
    movie_year: int
    movie_rating: float

def add_viewed_movie(raw_message: str) -> Viewed_Movie:
    pass


def movie_parser(raw_message):
    raw_text = raw_message.text
    movie_name = raw_text.split(',')[0]
    movie_year = raw_text.split(',')[1]
    return (movie_name, movie_year)

def movie_parser_triple(raw_message):
    raw_text = raw_message.text
    movie_name = raw_text.split(',')[0]
    movie_year = raw_text.split(',')[1]
    movie_rating = int(raw_text.split(',')[2])
    return (movie_name, movie_year, movie_rating)

def recommendation_movies_from_title(movie_name: str, movie_release_year: int) -> List[Recommend_Movie]:
    # Пример: Spider-Man, 2002
    sql = f"""
        select 
            rm.recommendation_film_title,
            rm.recommendation_film_year,
            rm.recommendation_film_rating
        from recommendation_movies rm
        where rm.film_title = "{movie_name}" and rm.film_year = {movie_release_year}
        order by rm.recommendation_film_rating desc
        --limit 10
    """
    cursor = db.get_cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    rec_movies = [Recommend_Movie(movie_title=row[0], movie_year=row[1], movie_rating=row[2]) for row in rows]
    return rec_movies

def recommendation_movies_from_history(movies_info):
    # movies_info = [ (Iron Man, 2008), (Spider-Man, 2002) ]
    if len(movies_info) == 0:
        return
    concat_movie = ''
    for el in movies_info:
        concat_movie += f"\'{el[0]}{el[1]}\'"+', '
    concat_movie = concat_movie[:-2]
    sql = f"""
            with tbl as (
            select
                rm.film_title,
                rm.film_year,
                rm.recommendation_film_title,
                rm.recommendation_film_year,
                rm.recommendation_film_rating
            from recommendation_movies rm
            where rm.film_title || rm.film_year in ({concat_movie})
            order by rm.recommendation_film_rating desc)
            select
                t.recommendation_film_title,
                t.recommendation_film_year,
                sum(t.recommendation_film_rating) as recommendation_film_rating
            from tbl t
            where t.recommendation_film_title || t.recommendation_film_year not in 
                (select distinct t.film_title || t.film_year from tbl t) 
            group by t.recommendation_film_title, t.recommendation_film_year
            order by 3 desc
        --limit 10
    """
    cursor = db.get_cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(rows)
    rec_movies = [Recommend_Movie(movie_title=row[0], movie_year=row[1], movie_rating=row[2]) for row in rows]
    print(rec_movies)
    return rec_movies

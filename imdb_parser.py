import requests as req
apikey = 'ebe0a211'


def get_movie_poster_url(imdb_id: str) -> str:
    url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={apikey}'
    resp = req.get(url)
    if resp.status_code == 200:
        return resp.json()["Poster"]
from telebot import types
import database_module as db
from imdb_parser import *
from aiogram.utils.markdown import *


def create_default_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button_next = types.InlineKeyboardButton(text="Ещё", callback_data="next_movie")
    button_stop = types.InlineKeyboardButton(text="Закончить", callback_data="stop_rec")
    keyboard.add(button_next, button_stop)
    return keyboard


def show_movie(movie_title, movie_year) -> (str, str):
    imdb_id = db.get_imdb_id(movie_title, movie_year)
    movie_info = db.movie_info(imdb_id)
    poster_url = get_movie_poster_url(imdb_id)
    caption_txt = text(
        f'<b><a href="https://www.imdb.com/title/{imdb_id}">{movie_info["movie_title"]}</a> ({movie_info["release_year"]})</b>\n'
        f'\n<b>Overview:</b>\n{movie_info["overview"]}')
    return caption_txt, poster_url

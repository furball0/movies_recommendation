import telebot
from aiogram.types import ParseMode
from aiogram.utils.markdown import *
from telebot import types
import database_module as db
import recommend_movie as rm
import function_module as fm

bot = telebot.TeleBot()


user_data = {}

states = {}
# default - 0
# waiting_movie_title - 1
# add movie - 2
# delete movie - 3


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    states[message.from_user.id] = 0
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}\n'
                                      f'<b>Этот бот имеет следующие команды:</b>\n'
                                      f'/recommend_movie_from_title - Рекомендации по фильму\n'
                                      f'/recommend_movie - Рекомендации по истории просмотров\n'
                                      f'/view_history - показать историю просмотренных фильмов\n'
                                      f'/add_movie - Добавить просмотренный фильм | Изменить рейтинг фильма\n'
                                      f'/delete_movie - Удалить просмотренный фильм\n',
                     parse_mode="HTML")


def is_exist(states, user_id, param):
    try:
        states[user_id] == param
    except KeyError:
        states[user_id] = 0
        return False
    return True


@bot.message_handler(commands=['view_history'])
def user_history(message):
    movies = db.get_user_history(message.from_user.id)
    if len(movies) == 0:
        bot.send_message(message.chat.id, text='Вы еще не добавили ни одного фильма')
        return

    txt = 'Вы посмотрели фильмы:\n'

    for i in range(len(movies)):
        movie_txt = f"""{i + 1}. {movies[i]['movie_title']} ({movies[i]['release_year']}) Rating: {movies[i]['user_vote_rating']}\n"""
        txt = text(txt, movie_txt)

    bot.send_message(message.chat.id, text=txt, parse_mode="HTML")


@bot.message_handler(commands=['recommend_movie_from_title'])
def get_movie_name(message):
    bot.send_message(message.chat.id,
                     text('Введите название и год выпуска фильма, по которому хотите получить рекомендации',
                          '\nПример: Spider-Man, 2002'))
    states[message.from_user.id] = 1  # перевед в статус ожидание названия фильма


@bot.message_handler(
    func=lambda message: is_exist(states, message.from_user.id, 1) and states[message.from_user.id] == 1)
def recommend_movies_from_title(message):
    # Проверка на корректность введения
    if len(message.text.split(',')) != 2:
        bot.send_message(message.chat.id,
                         text=f'Введите корректное названия фильма \nПример: Spider-Man, 2002')
        return
    movie_tuple = rm.movie_parser(message)

    # Создание словаря под пользователя
    try:
        user_data[message.from_user.id]["rec_movies"]
    except:
        user_data[message.from_user.id] = {}
    finally:
        user_data[message.from_user.id]["rec_movies"] = rm.recommendation_movies_from_title(movie_tuple[0],
                                                                                            movie_tuple[1])
    rec_movies = user_data[message.from_user.id]["rec_movies"]

    # Проверка, что фильм существует
    if len(rec_movies) == 0:
        bot.send_message(message.chat.id,
                         text=f'Такой фильм не найден. Попробуйте ввести другое название или проверьте корректность введенного названия')
        return

    print(rec_movies[0].movie_title, rec_movies[0].movie_year)
    caption_txt, poster_url = fm.show_movie(rec_movies[0].movie_title, rec_movies[0].movie_year)
    keyboard = fm.create_default_keyboard()
    bot.send_photo(message.chat.id, poster_url, caption=caption_txt, parse_mode="HTML", reply_markup=keyboard)

    user_data[message.from_user.id]["rec_movies"] = rec_movies[1:]
    print(user_data[message.from_user.id]["rec_movies"])


@bot.message_handler(commands=['recommend_movie'])
def recommend_movie(message):
    history = db.get_user_history(message.from_user.id)
    if len(history) == 0:
        bot.send_message(message.chat.id, text="Вы ещё не добавляли ни одного фильма")
        return
    movie_list = [(movie["movie_title"], movie["release_year"]) for movie in history]
    try:
        user_data[message.from_user.id]["rec_movies"]
    except:
        user_data[message.from_user.id] = {}
    finally:
        user_data[message.from_user.id]["rec_movies"] = rm.recommendation_movies_from_history(movie_list)
    rec_movies = user_data[message.from_user.id]["rec_movies"]
    print(rec_movies[0].movie_title, rec_movies[0].movie_year)
    caption_txt, poster_url = fm.show_movie(rec_movies[0].movie_title, rec_movies[0].movie_year)
    keyboard = fm.create_default_keyboard()
    bot.send_photo(message.chat.id, poster_url, caption=caption_txt, parse_mode="HTML", reply_markup=keyboard)

    user_data[message.from_user.id]["rec_movies"] = rec_movies[1:]
    print(user_data[message.from_user.id]["rec_movies"])


@bot.message_handler(commands=['add_movie'])
def get_name_add_movie(message):
    bot.send_message(message.chat.id,
                     text('Введите название, год выпуска фильма, рейтинг (от 0 до 10)',
                          '\nПример: Spider-Man, 2002, 9'))
    states[message.from_user.id] = 2


@bot.message_handler(
    func=lambda message: is_exist(states, message.from_user.id, 2) and states[message.from_user.id] == 2)
def add_movie(message):
    try:
        if message.text == 'End':
            states[message.from_user.id] = 0
    except:
        pass
    if len(message.text.split(',')) != 3:
        bot.send_message(message.chat.id,
                         text=f'Введите корректно данные \nПример: Spider-Man, 2002, 9\nЧтобы закончить напишите: End')
        return

    movie_tuple = rm.movie_parser_triple(message)
    if len(rm.recommendation_movies_from_title(movie_tuple[0], movie_tuple[1])) == 0:
        bot.send_message(message.chat.id,
                         text=f'Такого фильма не существует, попробуйте другой\nЧтобы закончить напишите: End')
        return
    db.insert_new_movie(message.from_user.id, db.get_imdb_id(movie_tuple[0], movie_tuple[1]), movie_tuple[2])
    # states[message.from_user.id] = 0
    bot.send_message(message.chat.id,
                     text=f'Фильм {movie_tuple[0]} ({str(movie_tuple[1]).strip()}) добавлен\nЧтобы закончить напишите: End')


@bot.message_handler(commands=['delete_movie'])
def get_name_del_movie(message):
    bot.send_message(message.chat.id,
                     text('Введите название, год выпуска фильма',
                          '\nПример: Spider-Man, 2002'))
    states[message.from_user.id] = 3


@bot.message_handler(
    func=lambda message: is_exist(states, message.from_user.id, 3) and states[message.from_user.id] == 3)
def del_movie(message):
    if len(message.text.split(',')) != 2:
        bot.send_message(message.chat.id,
                         text=f'Введите корректно данные \nПример: Spider-Man, 2002')
        return
    movie_tuple = rm.movie_parser(message)
    is_movie_exist = db.delete_viewed_movie(message.from_user.id, db.get_imdb_id(movie_tuple[0], movie_tuple[1]))
    if is_movie_exist:
        bot.send_message(message.chat.id, text=f'Фильм {movie_tuple[0]} ({str(movie_tuple[1]).strip()}) удалён')

    else:
        bot.send_message(message.chat.id,
                         text=f'Вы не добавляли фильм {movie_tuple[0]} ({str(movie_tuple[1]).strip()})')

    states[message.from_user.id] = 0


@bot.callback_query_handler(func=lambda call: call.data == "next_movie")
def show_next_movie(call: types.CallbackQuery):
    rec_movies = user_data[call.from_user.id]["rec_movies"]
    if len(rec_movies) == 0:
        return
    caption_txt, poster_url = fm.show_movie(rec_movies[0].movie_title, rec_movies[0].movie_year)
    keyboard = fm.create_default_keyboard()
    bot.send_photo(call.message.chat.id, poster_url, caption=caption_txt, parse_mode="HTML", reply_markup=keyboard)

    user_data[call.from_user.id]["rec_movies"] = rec_movies[1:]


@bot.callback_query_handler(func=lambda call: call.data == "stop_rec")
def stop_rec_movie(call: types.CallbackQuery):
    states[call.from_user.id] = 0
    user_data[call.from_user.id]["rec_movies"] = {}
    bot.send_message(call.message.chat.id, text="Рекомендации закончены")


@bot.message_handler(func=lambda message: message.text == 'fd')
def echo_all(message):
    # print(message)
    bot.reply_to(message, message.text)


@bot.message_handler(func=lambda message: True)
def unknown_message(message: types.Message):
    message_text = text('Я не знаю, что с этим делать',
                        italic('\nЯ просто напомню,'), 'что есть',
                        'команда', '/help')
    bot.reply_to(message, message_text, parse_mode=ParseMode.MARKDOWN)


bot.infinity_polling()

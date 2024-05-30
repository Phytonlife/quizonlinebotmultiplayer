import telebot
import requests
from googletrans import Translator
from html import unescape
from urllib.parse import unquote
from telebot import types

# Создаем экземпляр бота с указанием токена, который выдает @BotFather
bot = telebot.TeleBot("7095987405:AAET0MMPWkndGSTTh5LqiqtEgG2DM0VWGVU")

# Словарь для хранения информации о комнатах
rooms = {}


# Функция для получения вопросов из OpenTDB на английском языке
def get_trivia_questions():
    url = "https://opentdb.com/api.php"
    params = {
        "amount": 10,  # Количество вопросов
        "type": "multiple",  # Тип вопросов: multiple choice (с несколькими вариантами ответа)
        "encode": "url3986",  # Кодирование текста
        "lang": "en"  # Язык вопросов (английский)
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['results']


# Функция для перевода текста с английского на русский
def translate_text(text):
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='ru').text
    return translated_text


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_room_btn = types.KeyboardButton("Создать комнату")
    join_room_btn = types.KeyboardButton("Присоединиться к комнате")
    markup.add(create_room_btn, join_room_btn)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)


# Обработчик нажатия кнопок
@bot.message_handler(func=lambda message: message.text in ["Создать комнату", "Присоединиться к комнате"])
def handle_buttons(message):
    if message.text == "Создать комнату":
        create_room(message)
    elif message.text == "Присоединиться к комнате":
        join_room(message)


def create_room(message):
    room_id = str(message.chat.id) + "_" + str(message.message_id)
    rooms[room_id] = {"owner": message.from_user.username, "members": []}
    room_link = f"https://t.me/{bot.get_me().username}?start={room_id}"
    rooms[room_id]["link"] = room_link

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    join_room_btn = types.KeyboardButton(f"Присоединиться к комнате {message.from_user.username}")
    markup.add(join_room_btn)

    bot.send_message(message.chat.id, f"Комната создана! Ссылка для присоединения: {room_link}", reply_markup=markup)


def join_room(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for room_id, room_info in rooms.items():
        join_room_btn = types.KeyboardButton(f"Присоединиться к комнате {room_info['owner']}")
        markup.add(join_room_btn)
    if rooms:
        bot.send_message(message.chat.id, "Выберите комнату для присоединения:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Нет доступных комнат для присоединения.")


# Обработчик команды /start с параметром
@bot.message_handler(func=lambda message: message.text.startswith('/start ') and len(message.text.split()) == 2)
def join_specific_room(message):
    room_id = message.text.split()[1]
    if room_id in rooms:
        rooms[room_id]["members"].append(message.from_user.username)
        bot.send_message(message.chat.id, f"Вы присоединились к комнате {rooms[room_id]['owner']}.")
    else:
        bot.send_message(message.chat.id, "Комната не найдена или уже не существует.")


# Обработчик команды /quiz для начала викторины
@bot.message_handler(commands=['quiz'])
def quiz(message):
    if message.chat.id not in rooms:
        bot.send_message(message.chat.id,
                         "Вы не находитесь в комнате. Используйте команду /start для создания или присоединения к комнате.")
        return

    questions = get_trivia_questions()
    for question in questions:
        original_question = unescape(question['question'])  # Декодируем HTML
        translated_question = unquote(original_question)  # Удаляем символы %
        translated_question = translate_text(translated_question)  # Переводим текст на русский
        text = translated_question + "\n"
        answers = [unescape(answer) for answer in question['incorrect_answers']] + [
            question['correct_answer']]  # Декодируем HTML
        for i, answer in enumerate(answers, 1):
            original_answer = unescape(answer)  # Декодируем HTML
            translated_answer = unquote(original_answer)  # Удаляем символы %
            translated_answer = translate_text(translated_answer)  # Переводим текст на русский
            text += f"{i}. {translated_answer}\n"
        bot.send_message(message.chat.id, text)


# Запуск бота
bot.polling()

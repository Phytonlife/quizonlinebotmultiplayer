import telebot
import requests
from googletrans import Translator
from html import unescape
from urllib.parse import unquote

# Создаем экземпляр бота с указанием токена, который выдает @BotFather
bot = telebot.TeleBot("7095987405:AAET0MMPWkndGSTTh5LqiqtEgG2DM0VWGVU")

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
    questions = get_trivia_questions()
    for question in questions:
        original_question = unescape(question['question'])  # Декодируем HTML
        translated_question = unquote(original_question)  # Удаляем символы %
        translated_question = translate_text(translated_question)  # Переводим текст на русский
        text = translated_question + "\n"
        answers = [unescape(answer) for answer in question['incorrect_answers']] + [question['correct_answer']]  # Декодируем HTML
        for i, answer in enumerate(answers, 1):
            original_answer = unescape(answer)  # Декодируем HTML
            translated_answer = unquote(original_answer)  # Удаляем символы %
            translated_answer = translate_text(translated_answer)  # Переводим текст на русский
            text += f"{i}. {translated_answer}\n"
        bot.send_message(message.chat.id, text)

# Запуск бота
bot.polling()

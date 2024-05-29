import telebot
import requests

# Создаем экземпляр бота с указанием токена, который выдает @BotFather
bot = telebot.TeleBot("7095987405:AAET0MMPWkndGSTTh5LqiqtEgG2DM0VWGVU")

# Функция для получения вопросов из QuizAPI
def get_quiz_questions():
    url = "https://quizapi.io/api/v1/questions"
    params = {
        "apiKey": "YOUR_QUIZAPI_KEY",
        "limit": 10,  # Количество вопросов
        "category": "Рандомные вопросы",  # Категория вопросов (можно указать конкретную)
        "difficulty": "Easy",  # Уровень сложности
        "lang": "ru"  # Язык вопросов
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    questions = get_quiz_questions()
    for question in questions:
        text = f"{question['question']}\n"
        for i, answer in enumerate(question['answers'], 1):
            text += f"{i}. {answer['answer']}\n"
        bot.send_message(message.chat.id, text)

# Запуск бота
bot.polling()

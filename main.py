import telebot
from flask import Flask, request
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("api_key")
bot_key = os.getenv("bot_key")

bot = telebot.TeleBot(bot_key)
client = OpenAI(api_key=api_key)

app = Flask(__name__)

system_prompt = """
Ты — дружелюбный кулинарный ассистент. Люди пишут тебе, что у них есть в холодильнике, а ты предлагаешь несколько простых и вкусных рецепта из этих ингредиентов.
Ты отвечаешь коротко, понятно и по-русски. Добавь название блюда и список шагов.
Обращайся всегда на ты!
"""

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Напиши, что у тебя есть в холодильнике — я предложу рецепт 🍳')

@bot.message_handler(func=lambda message: True)
def chat_with_gpt(message):
    try:
        response = client.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {e}')

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid request', 400

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://recipe-gpt-bot.onrender.com')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


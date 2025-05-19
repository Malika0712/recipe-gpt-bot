import telebot
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("api_key")
bot_key = os.getenv("bot_key")

bot = telebot.TeleBot(bot_key)
client = OpenAI(api_key=api_key)

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

bot.infinity_polling()

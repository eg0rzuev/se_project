import telebot
import user_msgs
import os

print(os.environ.get('bot_token'))
bot = telebot.TeleBot(os.environ.get('bot_token'))


@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, user_msgs.start_message)


bot.infinity_polling()
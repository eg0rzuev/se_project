import telebot
import constants.queries
from constants.user_msgs import *
import constants.queries as queries
import os
from query_exec_funcs.exec_query import *
from query_exec_funcs.helper_funcs import *


bot = telebot.TeleBot(os.environ.get('bot_token'))


@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    print(message.text)
    bot.send_message(chat_id, user_msgs.start_message)


@bot.message_handler(commands=['add_me'])
def add_me_command(message):
    chat_id = message.chat.id
    user = message.from_user
    user_values = (user.id, user.username.lower(), user.first_name, user.last_name)
    try:
        user_in_chat = check_add_user_chat(chat_id, user, user_values)
        if user_in_chat == 0:
            bot.send_message(chat_id, user_msgs.user_added_to_group.format(username=user.username))
        else:
            bot.send_message(chat_id, user_msgs.user_already_in_group.format(username=user.username))
    except Exception as error:
        print(error)
        bot.send_message(chat_id, user_msgs.internal_db_error)


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    chat_id = message.chat.id
    try:
        if execute_query(queries.chat_exists, (chat_id,))[0][0] == 0:
            execute_query(queries.add_chat, (chat_id,))
        for user in message.new_chat_members:
            user_values = (user.id, user.username.lower(), user.first_name, user.last_name)
            user_in_chat = check_add_user_chat(chat_id, user, user_values)
            if user_in_chat == 0:
                bot.send_message(chat_id, user_msgs.user_added_to_group.format(username=user.username))
            else:
                bot.send_message(chat_id, user_msgs.user_already_in_group.format(username=user.username))
    except Exception as error:
        print(error)
        bot.send_message(chat_id, user_msgs.internal_db_error)


bot.infinity_polling()
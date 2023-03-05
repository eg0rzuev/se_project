import telebot
from telebot import TeleBot

import constants.queries
from constants.user_msgs import *
import constants.queries as queries
import os
from query_exec_funcs.exec_query import *
import time
from query_exec_funcs.helper_funcs import *


bot: TeleBot = telebot.TeleBot(os.environ.get('bot_token'), parse_mode="MARKDOWN")


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
        if not user_in_chat:
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
            if not user_in_chat:
                bot.send_message(chat_id, user_msgs.user_added_to_group.format(username=user.username))
            else:
                bot.send_message(chat_id, user_msgs.user_already_in_group.format(username=user.username))
    except Exception as error:
        print(error)
        bot.send_message(chat_id, user_msgs.internal_db_error)


@bot.message_handler(commands=['add_loan'], content_types=['text'])
def add_loan_command(message):
    chat_id = message.chat.id
    text_arr = message.text.split()
    try:
        if len(text_arr) < 4:
            bot.send_message(chat_id, user_msgs.wrong_param_num)
            return
        if text_arr[1][0] != '@' or text_arr[2][0] != '@':
            bot.send_message(chat_id, user_msgs.uname_et_symbol)
            return
        unames = [text_arr[1][1:].lower(), text_arr[2][1:].lower()]
        print(text_arr[4:])
        notes = " ".join(text_arr[4:])
        user_ids = []
        amount = text_arr[3]
        if not is_valid_amount(amount):
            bot.send_message(chat_id, user_msgs.invalid_amount)
            return
        amount = to_common_float(amount)
        for username in unames:
            if len(username) < 5 or len(username) > 32:
                bot.send_message(chat_id, user_msgs.uname_too_short)
                return
            user_id = get_uid(username)
            if not user_id:
                bot.send_message(chat_id, user_msgs.user_not_in_group.format(username=username))
                return
            user_ids.append(user_id)
        change_balance(user_ids[0], chat_id, -amount)
        change_balance(user_ids[1], chat_id, amount)
        execute_query(queries.add_transaction, (chat_id, amount, user_ids[1], user_ids[0], round(time.time()), notes))
        bot.send_message(chat_id, user_msgs.balance_change.format(usr0=unames[0], usr1=unames[1], amount=amount))
    except Exception as error:
        bot.send_message(chat_id, user_msgs.internal_db_error)
        print(error)

@bot.message_handler(commands=['current_state'])
def curr_state_command(message):
    chat_id = message.chat.id
    try:
        query_res = execute_query(queries.curr_state, (chat_id,))
        if not query_res:
            bot.send_message(chat_id, user_msgs.empty_group)
            return
        print(query_res)
        output_msg = beautify_balance_output(query_res)
        bot.send_message(chat_id, output_msg)
    except Exception as error:
        bot.send_message(chat_id, user_msgs.internal_db_error)
        print(error)

@bot.message_handler(commands=['show_transactions'])
def show_transactions(message):
    chat_id = message.chat.id
    query_res = execute_query(queries.get_transactions, (chat_id,))
    output_msg = beautify_transactions_output(query_res)
    bot.send_message(chat_id, output_msg)



bot.infinity_polling()
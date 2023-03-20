import telebot
from telebot import TeleBot
from telebot import types
from constants.user_msgs import msgs
from constants.common_constants import *
import constants.queries as queries
import os
from query_exec_funcs.exec_query import *
import time
from query_exec_funcs.helper_funcs import *

bot: TeleBot = telebot.TeleBot(os.environ.get('bot_token'), parse_mode="MARKDOWN")


@bot.message_handler(commands=['start'])
def start_command(message):
    lang = EN
    try:
        chat_id = message.chat.id
        #print(message.text)
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        #print(lang)
        bot.send_message(chat_id, msgs[START_MESSAGE][lang])
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])


@bot.message_handler(commands=['set_lang'])
def set_lang(message):
    curr_lang = EN
    try:
        chat_id = message.chat.id
        text_arr = message.text.split()
        curr_lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        if len(text_arr) < 2:
            bot.send_message(chat_id, msgs[specify_the_language][curr_lang])
            return
        new_lang = text_arr[1]
        if new_lang not in LANGUAGES:
            bot.send_message(chat_id, msgs[lang_not_supported][curr_lang].format(lang=new_lang))
            return
        #print("NEW LANG = {}".format(new_lang))
        execute_query(queries.set_chat_lang, (new_lang, chat_id))
        bot.send_message(chat_id, msgs[lang_changed][new_lang].format(lang0=curr_lang,lang1=new_lang))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][curr_lang])



@bot.message_handler(commands=['add_me'])
def add_me_command(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        user = message.from_user
        user_values = (user.id, user.username.lower(), user.first_name, user.last_name)
        user_in_chat = check_add_user_chat(chat_id, user, user_values)
        if not user_in_chat:
            bot.send_message(chat_id, msgs[user_added_to_group][lang].format(username=user.username))
        else:
            bot.send_message(chat_id, msgs[user_already_in_group][lang].format(username=user.username))
    except Exception as error:
        #print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        if execute_query(queries.chat_exists, (chat_id,))[0][0] == 0:
            execute_query(queries.add_chat, (chat_id,))
        for user in message.new_chat_members:
            user_values = (user.id, user.username.lower(), user.first_name, user.last_name)
            user_in_chat = check_add_user_chat(chat_id, user, user_values)
            if not user_in_chat:
                bot.send_message(chat_id, msgs[user_added_to_group][lang].format(username=user.username))
            else:
                bot.send_message(chat_id, msgs[user_already_in_group][lang].format(username=user.username))
    except Exception as error:
        #print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])


@bot.message_handler(commands=['loan_oneline'], content_types=['text'])
def add_loan_command(message):
    lang = EN
    try:
        #get the chat id
        chat_id = message.chat.id
        #get chat language
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        #get the message text in a form of list, the element at index 0 is always the command
        text_arr = message.text.split()
        #at least 4 obligatory arguments are expected: command, borrower uname, lender uname, amount
        #comments are optional
        if len(text_arr) < 4:
            bot.send_message(chat_id, msgs[wrong_param_num][lang])
            return
        brrwr_uname = text_arr[1][1:] if text_arr[1][0] == '@' else text_arr[1]
        lndr_uname = text_arr[2][1:] if text_arr[2][0] == '@' else text_arr[2]
        unames = [brrwr_uname.lower(), lndr_uname.lower()]
        #print(text_arr[4:])
        notes = " ".join(text_arr[4:])
        user_ids = []
        amount = text_arr[3]
        if not is_valid_amount(amount):
            bot.send_message(chat_id, msgs[invalid_amount][lang])
            return
        amount = to_common_float(amount)
        for username in unames:
            if len(username) < 5 or len(username) > 32:
                bot.send_message(chat_id, msgs[uname_too_short][lang])
                return
            user_id = get_uid(username)
            if not user_id:
                bot.send_message(chat_id, msgs[user_not_in_group][lang].format(username=username))
                return
            user_ids.append(user_id)
        change_balance(user_ids[0], chat_id, -amount)
        change_balance(user_ids[1], chat_id, amount)
        execute_query(queries.add_transaction, (chat_id, amount, user_ids[1], user_ids[0], round(time.time()), notes))
        bot.send_message(chat_id, msgs[balance_change][lang].format(usr0=unames[0], usr1=unames[1], amount=amount))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        #print(error)

@bot.message_handler(commands=['current_state'])
def curr_state_command(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        query_res = execute_query(queries.curr_state, (chat_id,))
        if not query_res:
            bot.send_message(chat_id, msgs[empty_group][lang])
            return
        #print(query_res)
        output_msg = beautify_balance_output(query_res, lang)
        bot.send_message(chat_id, output_msg)
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        #print(error)

@bot.message_handler(commands=['show_transactions'])
def show_transactions(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        query_res = execute_query(queries.get_transactions, (chat_id,))
        output_msg = tabulate(query_res, headers=["lender", "borrower", "amount", "date time", "notes"], tablefmt='orgtbl')
        bot.send_message(chat_id, output_msg)
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        #print(error)


@bot.message_handler(commands=['finalize'])
def finalize_command(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        query_res = [list(x) for x in execute_query(queries.all_balance, (chat_id,))]
        query_res.sort(key=lambda x: x[1])
        if round(sum([x[1] for x in query_res]), 2) != 0:
            bot.send_message(chat_id, msgs[integrity_error][lang])
            return
        left, right = 0, len(query_res) - 1
        res = []
        while left < right:
            if abs(query_res[left][1]) >= query_res[right][1]:
                res.append((query_res[left][0], query_res[right][0], query_res[right][1]))
                query_res[left][1] += query_res[right][1]
                query_res[right][1] = 0
            else:
                res.append((query_res[left][0], query_res[right][0], -query_res[left][1]))
                query_res[right][1] += query_res[left][1]
                query_res[left][1] = 0
            if query_res[right][1] == 0:
                right -= 1
            if query_res[left][1] == 0:
                left += 1
        bot.send_message(chat_id, beautify_finilize(res, lang))
    except Exception as error:
        #print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])


@bot.message_handler(commands=['new_loan'])
def new_loan(message):
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        markup = types.ForceReply(selective=False)
        lender_msg_id = bot.send_message(chat_id, msgs[enter_lender_uname][lang], reply_markup=markup).message_id
        execute_query(queries.temp_tr_insert_lender_msg_id, (lender_msg_id,chat_id))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        #print(error)



@bot.message_handler(func=lambda message: True)
def new_loan_handler(message):
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        markup = types.ForceReply(selective=False)
        if not message.reply_to_message:
            return
        reply_id = message.reply_to_message.message_id
        reply_text = message.reply_to_message.text
        #print(reply_id)
        if reply_text == msgs[enter_lender_uname][lang] and execute_query(queries.lend_msg_in_temp_tr, (reply_id, chat_id))[0][0] == 1:
            if len(message.text.split()) > 1:
                bot.send_message(chat_id, msgs[enter_only_username][lang])
                return
            lender_uname = message.text[1:] if message.text[0] == '@' else message.text
            if not execute_query(queries.get_user_id, (lender_uname,)):
                bot.send_message(chat_id, msgs[user_not_in_group][lang].format(username=lender_uname))
                return
            borrower_msg_id = bot.send_message(chat_id, msgs[enter_brrwr_uname][lang], reply_markup=markup).message_id
            execute_query(queries.temp_tr_update_lender, (lender_uname, borrower_msg_id, reply_id, chat_id))
        if reply_text == msgs[enter_brrwr_uname][lang] and execute_query(queries.borr_msg_in_temp_tr, (reply_id, chat_id))[0][0] == 1:
            if len(message.text.split()) > 1:
                bot.send_message(chat_id, msgs[enter_only_username])
                return
            borrower_uname = message.text[1:] if message.text[0] == '@' else message.text
            if not execute_query(queries.get_user_id, (borrower_uname,)):
                bot.send_message(chat_id, msgs[user_not_in_group][lang].format(username=borrower_uname))
                return
            amount_msg_id = bot.send_message(chat_id, msgs[enter_amount][lang], reply_markup=markup).message_id
            execute_query(queries.temp_tr_update_borrower, (borrower_uname, amount_msg_id, reply_id, chat_id))
        if reply_text == msgs[enter_amount][lang] and execute_query(queries.amount_msg_in_temp_tr, (reply_id, chat_id))[0][0] == 1:
            if len(message.text.split()) > 1:
                bot.send_message(chat_id, msgs[enter_only_amount][lang])
                return
            amount = message.text
            amount_msg_id = reply_id
            if not is_valid_amount(amount):
                bot.send_message(chat_id, msgs[invalid_amount][lang])
                return
            amount = to_common_float(amount)
            execute_query(queries.temp_tr_update_amount, (amount, reply_id, chat_id))
            execute_query(queries.insert_transaction, (reply_id, chat_id))
            q_res = execute_query(queries.uid_from_temp_tr, (amount_msg_id, chat_id))
            #print(q_res[0])
            lender_uid, borrower_uid = q_res[0][0], q_res[0][1]
            lender_uname = execute_query(queries.get_username, (lender_uid,))[0][0]
            borrower_uname = execute_query(queries.get_username, (borrower_uid,))[0][0]
            change_balance(borrower_uid, chat_id, -amount)
            change_balance(lender_uid, chat_id, amount)
            bot.send_message(chat_id, msgs[balance_change][lang].format(usr0=borrower_uname, usr1=lender_uname, amount=amount))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        #print("NEW LOAN HANDLER")
        #print(error)


bot.infinity_polling()
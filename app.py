import telebot
from telebot import TeleBot
from telebot import types
from constants.user_msgs import msgs
from constants.common_constants import *
import constants.queries as queries
import os
from query_exec_funcs.exec_query import *
from datetime import datetime
import time
from query_exec_funcs.helper_funcs import *

#initializing the bot
bot: TeleBot = telebot.TeleBot(os.environ.get('bot_token'), parse_mode="HTML")

#This command is used to initialize the chat and test if the bot is working and replying to the user
@bot.message_handler(commands=['start'])
def start_command(message):
    lang = EN
    try:
        chat_id = message.chat.id
        chat_exists = execute_query(queries.chat_exists, (chat_id,))[0][0]
        if chat_exists == 0:
            execute_query(queries.add_chat, (chat_id, ))
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        bot.send_message(chat_id, msgs[START_MESSAGE][lang])
    except Exception as error:
        print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])

#set the language of the group, curr languages are it, ru, en
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
        execute_query(queries.set_chat_lang, (new_lang, chat_id))
        bot.send_message(chat_id, msgs[lang_changed][new_lang].format(lang0=curr_lang,lang1=new_lang))
    except Exception as error:
        print(error)
        bot.send_message(chat_id, msgs[internal_db_error][curr_lang])


#add the command sender to the group, which means that the user is added to the users table
#user - chat pair added to the users_chats table
@bot.message_handler(commands=['add_me'])
def add_me_command(message):
    lang = EN
    try:
        print(message)
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        user = message.from_user
        if not user.username:
            uname = generate_username()
            print(uname)
            bot.send_message(chat_id, msgs[UNAME_GENERATED][lang].format(uname=uname, fname=user.first_name))
        else:
            uname = user.username
        user_values = (user.id, uname.lower(), user.first_name, user.last_name)
        user_in_chat = check_add_user_chat(chat_id, user, user_values)
        if not user_in_chat:
            bot.send_message(chat_id, msgs[user_added_to_group][lang].format(username=uname))
        else:
            if not user.username:
                uname = execute_query(queries.get_username, (user.id,))
            else:
                uname = user.username
            bot.send_message(chat_id, msgs[user_already_in_group][lang].format(username=uname))
    except Exception as error:
        print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])

#a handler of a new member message type, very similar to the previous function
@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        if execute_query(queries.chat_exists, (chat_id,))[0][0] == 0:
            execute_query(queries.add_chat, (chat_id,))
        for user in message.new_chat_members:
            print(user)
            if not user.username:
                uname = generate_username()
                print(uname)
                while execute_query(queries.check_uname_in_chat, (uname,))[0][0] == 1:
                    uname = generate_username()
                print(uname)
                bot.send_message(chat_id, msgs[UNAME_GENERATED][lang].format(uname=uname,fname=user.first_name))
            else:
                uname = user.username
            user_values = (user.id, uname.lower(), user.first_name, user.last_name)
            user_in_chat = check_add_user_chat(chat_id, user, user_values)
            if not user_in_chat:
                bot.send_message(chat_id, msgs[user_added_to_group][lang].format(username=uname))
            else:
                if not user.username:
                    uname = execute_query(queries.get_username, (user.id,))
                else:
                    uname = user.username
                bot.send_message(chat_id, msgs[user_already_in_group][lang].format(username=uname))
    except Exception as error:
        print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])

#add loan in a following format: /loan_oneline @brwr @lender 1000
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
        execute_query(queries.add_transaction, (chat_id, amount, user_ids[1], user_ids[0], notes))
        bot.send_message(chat_id, msgs[balance_change][lang].format(usr0=unames[0], usr1=unames[1], amount=amount))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        print(error)

# display all users' balance
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
        print(error)

#show transactions
@bot.message_handler(commands=['show_transactions'])
def show_transactions(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        query_res = execute_query(queries.get_transactions, (chat_id,))
        print(query_res)
        for i, row in enumerate(query_res):
            row = list(row)
            #print(row[3].replace(second=0,microsecond=0))
            row[3] = row[3].replace(second=0, microsecond=0)
            print(row[3])
            query_res[i] = tuple(row)
        output_msg = "<pre>" + tabulate(query_res, headers=["lender", "borrower", "amount", "date time", "notes"]) + "</pre>"
        print(output_msg)
        #output_msg = transactions_output(query_res)
        bot.send_message(chat_id, output_msg)
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        print(error)

#print a message what amount needs to be transfered so that everybody gets a 0 balance
#two pointers method is used
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
        print(error)
        bot.send_message(chat_id, msgs[internal_db_error][lang])

#new loan but in a interactive way
@bot.message_handler(commands=['new_loan'])
def new_loan(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        markup = types.ForceReply(selective=False)
        lender_msg_id = bot.send_message(chat_id, msgs[enter_lender_uname][lang], reply_markup=markup).message_id
        execute_query(queries.temp_tr_insert_lender_msg_id, (lender_msg_id,chat_id))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        print(error)


#handles the replies to insert the replies
@bot.message_handler(func=lambda message: True)
def new_loan_handler(message):
    lang = EN
    try:
        chat_id = message.chat.id
        lang = execute_query(queries.get_chat_lang, (chat_id,))[0][0]
        markup = types.ForceReply(selective=False)
        #only messages that are replies are interesting
        if not message.reply_to_message:
            return
        reply_id = message.reply_to_message.message_id
        reply_text = message.reply_to_message.text
        print(execute_query(queries.lend_msg_in_temp_tr, (reply_id, chat_id))[0][0])
        #check is reply message is referring to "enter lender name", the message was sent by the bot and no lender name is entered
        if reply_text in msgs[enter_lender_uname].values() and execute_query(queries.lend_msg_in_temp_tr, (reply_id, chat_id))[0][0] == 1:
            #check if only one word is entered
            if len(message.text.split()) > 1:
                bot.send_message(chat_id, msgs[enter_only_username][lang])
                return
            print()
            #username can be entered as "@username"or simply as "username"
            lender_uname = message.text[1:] if message.text[0] == '@' else message.text
            #check if the message is actually a username
            if not execute_query(queries.get_user_id, (lender_uname,)):
                bot.send_message(chat_id, msgs[user_not_in_group][lang].format(username=lender_uname))
                return
            #save the id of the message the bot replies with a
            borrower_msg_id = bot.send_message(chat_id, msgs[enter_brrwr_uname][lang], reply_markup=markup).message_id
            #update the field "lender_uid" using lender_uname, update borrower_msg_id based on unique chat_id, reply_id pair
            execute_query(queries.temp_tr_update_lender, (lender_uname, borrower_msg_id, reply_id, chat_id))
        #check is reply message is referring to "enter brwr name", the message was sent by the bot and no brwr name is entered
        #other steps are pretty similar to previous if condition
        if reply_text in msgs[enter_brrwr_uname].values() and execute_query(queries.borr_msg_in_temp_tr, (reply_id, chat_id))[0][0] == 1:
            if len(message.text.split()) > 1:
                bot.send_message(chat_id, msgs[enter_only_username])
                return
            borrower_uname = message.text[1:] if message.text[0] == '@' else message.text
            if not execute_query(queries.get_user_id, (borrower_uname,)):
                bot.send_message(chat_id, msgs[user_not_in_group][lang].format(username=borrower_uname))
                return
            amount_msg_id = bot.send_message(chat_id, msgs[enter_amount][lang], reply_markup=markup).message_id
            execute_query(queries.temp_tr_update_borrower, (borrower_uname, amount_msg_id, reply_id, chat_id))
        #check is reply message is referring to "enter amount", the message was sent by the bot and no amount is entered
        if reply_text in msgs[enter_amount].values() and execute_query(queries.amount_msg_in_temp_tr, (reply_id, chat_id))[0][0] == 1:
            if len(message.text.split()) > 1:
                bot.send_message(chat_id, msgs[enter_only_amount][lang])
                return
            amount = message.text
            amount_msg_id = reply_id
            #check if amount is a valid number, float with . or , and no more than 2 numbers after . or ,
            if not is_valid_amount(amount):
                bot.send_message(chat_id, msgs[invalid_amount][lang])
                return
            #transform to common float with "."
            amount = to_common_float(amount)
            #add amount to temp_transactions
            execute_query(queries.temp_tr_update_amount, (amount, reply_id, chat_id))
            #transfer the data to transactions
            execute_query(queries.insert_transaction, (reply_id, chat_id))
            #get lender, borrower user ids for the bot message
            q_res = execute_query(queries.uid_from_temp_tr, (amount_msg_id, chat_id))
            lender_uid, borrower_uid = q_res[0][0], q_res[0][1]
            #get their usernames
            lender_uname = execute_query(queries.get_username, (lender_uid,))[0][0]
            borrower_uname = execute_query(queries.get_username, (borrower_uid,))[0][0]
            #change balance of users
            change_balance(borrower_uid, chat_id, -amount)
            change_balance(lender_uid, chat_id, amount)
            #tell user that the balance was changes
            bot.send_message(chat_id, msgs[balance_change][lang].format(usr0=borrower_uname, usr1=lender_uname, amount=amount))
    except Exception as error:
        bot.send_message(chat_id, msgs[internal_db_error][lang])
        print(error)


bot.infinity_polling()
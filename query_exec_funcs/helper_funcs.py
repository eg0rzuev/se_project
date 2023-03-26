from constants import queries
from query_exec_funcs.exec_query import *
import re
from datetime import datetime
from constants.common_constants import *
from constants.user_msgs import msgs
import random
from datetime import datetime
from tabulate import tabulate
#import constants.user_msgs

def is_user_in_chat(user_id, chat_id):
    user_in_chat = execute_query(queries.user_chat_exists, (user_id, chat_id))[0][0]
    return not(user_in_chat == 0)



def check_add_user_chat(chat_id, user, user_values):
    if execute_query(queries.chat_exists, (chat_id,))[0][0] == 0:
        execute_query(queries.add_chat, (chat_id,))
    if execute_query(queries.user_exists, (user.id,))[0][0] == 0:
        execute_query(queries.add_user, user_values)
    user_in_chat = is_user_in_chat(user.id, chat_id)
    if not user_in_chat:
        execute_query(queries.add_user_chat, (user.id, chat_id))
    return user_in_chat


def is_valid_amount(num):
    if re.match(r"^[0-9]+([,.][0-9]{1,2})?$", num):
        return True
    return False


def get_uid(username):
    try:
        return execute_query(queries.get_user_id, (username,))[0][0]
    except IndexError as e:
        return None
    except Exception as e:
        print(e)
        raise e

def change_balance(user_id, chat_id, balance_diff):
    try:
        query_res = execute_query(queries.get_user_balance, (user_id, chat_id))
        old_balance = query_res[0][0]
        new_balance = old_balance + balance_diff
        execute_query(queries.change_balance, (new_balance, user_id, chat_id))
    except Exception as error:
        print(error)
        raise error


def to_common_float(num):
    num = num.replace(",", ".", 1)
    return float(num)

def beautify_balance_output(data_rows, lang=EN):
    output_msg = msgs[users_balance_bold][lang] + "\n"
    for user, amount in data_rows:
        output_msg += msgs[uname_balance][lang].format(user=user, amount=amount) + "\n"
    return output_msg


def format_unix_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

def beautify_transactions_output(data_rows, lang=EN):
    output = msgs[transactions_header][lang]
    print(output)
    for row in data_rows:
        lender_uname, borrower_uname, amount, unix_date, notes = row
        print(unix_date)
        date_time = format_unix_time(unix_date)
        output += msgs[transactions_values][lang].format(lender_uname, borrower_uname, amount, date_time, notes)
    return output

def beautify_finilize(arr, lang=EN):
    output_msg = ""
    for user1, user2, amount in arr:
        output_msg += msgs[has_to_transfer][lang].format(user1=user1, user2=user2, amount=round(amount,2)) + "\n"
    return output_msg


def generate_username():
    with open("constants/temp_unames.txt", "r") as f:
        words = [word.strip() for word in f.readlines()]
    username = random.choice(words)
    return username






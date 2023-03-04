from constants import queries
from query_exec_funcs.exec_query import *


def check_add_user_chat(chat_id, user, user_values):
    if execute_query(queries.chat_exists, (chat_id,))[0][0] == 0:
        execute_query(queries.add_chat, (chat_id,))
    if execute_query(queries.user_exists, (user.id,))[0][0] == 0:
        execute_query(queries.add_user, user_values)
    user_in_chat = execute_query(queries.user_chat_exists, (user.id, chat_id))[0][0]
    if user_in_chat == 0:
        execute_query(queries.add_user_chat, (user.id, chat_id))
    return user_in_chat
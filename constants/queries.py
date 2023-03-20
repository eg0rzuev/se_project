add_user = """  INSERT INTO users
                (user_id, username, first_name, last_name) 
                VALUES 
                (%s,%s,%s,%s);
"""
add_chat = """  INSERT INTO chats
                (chat_id) 
                VALUES 
                (%s);
"""
chat_exists = """   SELECT COUNT(1)
                    FROM chats
                    WHERE chat_id = %s;
"""
user_exists = """   SELECT COUNT(1)
                    FROM users
                    WHERE user_id = %s;
"""
user_chat_exists = """  SELECT COUNT(1)
                        FROM users_chats
                        WHERE user_id = %s and chat_id = %s;
"""
add_user_chat = """ INSERT INTO users_chats
                    (user_id, chat_id)
                    VALUES 
                    (%s,%s);
"""
get_user_id = """   SELECT user_id
                    FROM users
                    WHERE username = %s;
"""
get_user_balance = """  SELECT balance
                        FROM users_chats
                        WHERE user_id = %s and chat_id = %s;
"""
change_balance = """UPDATE users_chats
                    SET balance = %s
                    WHERE user_id = %s AND chat_id = %s;
"""
add_transaction = """   INSERT INTO transactions 
                        (chat_id, amount, lender, borrower, notes, date_time)
                        VALUES
                        (%s,%s,%s,%s,%s,NOW());
"""
curr_state = """    SELECT username, balance
                    FROM users_chats 
                    INNER JOIN users u ON u.user_id = users_chats.user_id
                    WHERE users_chats.chat_id = %s;
"""
get_transactions = """  SELECT u1.username as lender_uname, u2.username as borrower_uname, amount, date_time, notes
                        FROM transactions 
                        INNER JOIN users u1 ON lender = u1.user_id
                        INNER JOIN users u2 ON borrower = u2.user_id
                        WHERE chat_id = %s;
"""
all_balance = """   SELECT username, balance
                    FROM users_chats 
                    INNER JOIN users u 
                    ON u.user_id = users_chats.user_id
                    WHERE chat_id = %s;
"""
temp_tr_insert_lender_msg_id = """  INSERT INTO temp_transactions
                                    (lender_msg_id, chat_id, date_time)
                                    VALUES 
                                    (%s, %s, NOW());
"""
temp_tr_update_lender = """ UPDATE temp_transactions
                            SET lender_uid = (SELECT user_id FROM users WHERE username = %s), 
                                borrower_msg_id = %s
                            WHERE lender_msg_id = %s AND chat_id = %s;
"""
#TODO
temp_tr_update_borrower = """   UPDATE temp_transactions
                                SET borrower_uid = (SELECT user_id FROM users WHERE username = %s),
                                    amount_msg_id = %s
                                WHERE borrower_msg_id = %s AND chat_id = %s;
"""
temp_tr_update_amount = """ UPDATE temp_transactions
                            SET amount = %s 
                            WHERE amount_msg_id = %s AND chat_id = %s;
"""
insert_transaction = """    INSERT INTO transactions
                            (lender, borrower, chat_id, amount, date_time)
                            SELECT
                            lender_uid, borrower_uid, chat_id, amount, NOW()
                            FROM
                            temp_transactions
                            WHERE amount_msg_id = %s AND chat_id = %s;
"""
borr_msg_in_temp_tr  = """  SELECT COUNT(1)
                            FROM temp_transactions
                            WHERE borrower_msg_id = %s AND chat_id = %s;
"""
lend_msg_in_temp_tr = """   SELECT COUNT(1)
                            FROM temp_transactions
                            WHERE lender_msg_id = %s AND chat_id = %s;
"""
amount_msg_in_temp_tr = """ SELECT COUNT(1)
                            FROM temp_transactions
                            WHERE amount_msg_id = %s AND chat_id = %s;
"""
uid_from_temp_tr = """  SELECT lender_uid, borrower_uid
                        FROM temp_transactions
                        WHERE amount_msg_id = %s AND chat_id = %s;
"""
get_username = """  SELECT username
                    FROM users
                    WHERE user_id = %s;
"""
get_chat_lang = """ SELECT language
                    FROM chats
                    WHERE chat_id = %s;
"""
set_chat_lang = """ UPDATE chats
                    SET language = %s 
                    WHERE chat_id = %s;
"""
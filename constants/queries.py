add_user = """  INSERT INTO users
                (user_id, username, first_name, last_name) 
                VALUES 
                (%s,%s,%s,%s);"""
add_chat = """  INSERT INTO chats
                (chat_id) 
                VALUES 
                (%s);"""
chat_exists = """   SELECT COUNT(1)
                    FROM chats
                    WHERE chat_id = %s;"""
user_exists = """   SELECT COUNT(1)
                    FROM users
                    WHERE user_id = %s;"""
user_chat_exists = """  SELECT COUNT(1)
                        FROM users_chats
                        WHERE user_id = %s and chat_id = %s;
"""
add_user_chat = """ INSERT INTO users_chats
                    (user_id, chat_id)
                    VALUES 
                    (%s,%s);"""
get_user_id = """   SELECT user_id
                    FROM users
                    WHERE username = %s;"""
get_user_balance = """  SELECT balance
                        FROM users_chats
                        WHERE user_id = %s and chat_id = %s;"""
change_balance = """UPDATE users_chats
                    SET balance = %s
                    WHERE user_id = %s AND chat_id = %s;"""
add_transaction = """   INSERT INTO transactions 
                        (chat_id, amount, lender, borrower, date_time, notes)
                        VALUES
                        (%s,%s,%s,%s,%s,%s);"""
curr_state = """    SELECT username, balance
                    FROM users_chats 
                    INNER JOIN users u ON u.user_id = users_chats.user_id
                    WHERE users_chats.chat_id = %s;"""
get_transactions = """  SELECT u1.username as lender_uname, u2.username as borrower_uname, amount, date_time, notes
                        FROM transactions 
                        INNER JOIN users u1 ON lender = u1.user_id
                        INNER JOIN users u2 ON borrower = u2.user_id
                        WHERE chat_id = %s;"""
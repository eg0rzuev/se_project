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
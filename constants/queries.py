add_user = """  INSERT INTO Users
                (user_id, username, first_name, last_name) 
                VALUES 
                (%s,%s,%s,%s);"""
add_chat = """  INSERT INTO Chats
                (chat_id) 
                VALUES 
                (%s);"""
chat_exists = """   SELECT COUNT(1)
                    FROM Chats
                    WHERE chat_id = %s;"""
user_exists = """   SELECT COUNT(1)
                    FROM Users
                    Where user_id = %s;"""
add_user_chat = """ INSERT INTO UsersChats
                    (user_id, chat_id)
                    VALUES 
                    (%s,%s);"""
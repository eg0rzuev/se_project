import psycopg2
from constants import user_msgs
#from constants.queries import *
import os


db_host = os.environ.get("db_host")
db_name = os.environ.get("database")
db_user = os.environ.get("db_user")
db_pwd = os.environ.get("db_pwd")

def execute_query(query, query_params):
    output_data = []
    try:
        conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_pwd)
        cursor = conn.cursor()
        cursor.execute(query, query_params)
        if cursor.description is not None:
            output_data = cursor.fetchall()
        conn.commit()
        cursor.close()
    except psycopg2.IntegrityError as error:
        print("Integrity error!")
        print(error)
        raise error
    except Exception as error:
        print("Some other error!")
        print(error)
        raise error
    finally:
        if conn:
            conn.close()
        return output_data
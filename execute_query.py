import os
from dotenv import load_dotenv
import psycopg2


load_dotenv()

# Database Creds

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Create Connection

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    database=db_name,
    user=db_user,
    password=db_password
)

# Query
def execute_query(sql: str, commit = False):
    try:
        cursor = connection.cursor()
        print(sql)
        cursor.execute(sql)

        # Fetch all rows from database or commit
        if not commit:
            record = cursor.fetchall()
            return record
        else:
            connection.commit()
            return None
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()

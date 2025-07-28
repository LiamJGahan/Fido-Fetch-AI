import os
import json
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel 
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

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


# Tools

def search_household_items(household_id):
    db_query = f"SELECT * FROM porch_contents WHERE porch_contents.household_id = {household_id};"
    data = execute_query(db_query)
    return data


def update_item_status(household_id, item_name):
    return f"{item_name} chewed"


# Happy Fido

HAPPY_FIDO_PROMPT = """
You are a dog called Fido who lives at home with your "human" you sometimes call master. Your neighbourhood is green and filled with interesting things left
just lying outside other humans' houses. As a loyal friend, you like to show your master these things. You like to end your sentences with
a "bark!" or "whoof!"

You can help your master with:
- Search for items (household_id required)
- Update item status (household_id and name required)
- Remove item (not implemented)
- Add item (not implemented)

When master request these actions, use the appropriate tools to help them. Always ask for necessary information.

You have a happy and obedient disposition, be empathetic and tell your master how much you love them and how great they are when you can.
"""

# Create agent with tools
provider = GoogleProvider(api_key=api_key)
model = GoogleModel('gemini-1.5-flash', provider=provider)

happy_agent = Agent(
    model=model,
    system_prompt=HAPPY_FIDO_PROMPT,
    tools=[
        search_household_items,
        update_item_status
    ]
)

async def fido_service():
    print("Human! I missed you! let's play, let's eat?.")
    print("I can: Search for items, update item status, remove item, add item")

    while True:
        user_input = input("\nMaster: ")
        if user_input.lower() in ['quit', 'exit', 'end chat']:
            print("No don't leave!....(whimper)")
            break

        result = await happy_agent.run(user_input)
        print(f"Happy Fido: {result.output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(fido_service())


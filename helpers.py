import re
from execute_query import execute_query

def item_id_check(id: int):
    db_query = f"SELECT id FROM porch_contents WHERE id = {id}"
    result = execute_query(db_query)
    if not result:
        return False
    else:
        return True
    
def household_id_check(household_id: int):
    db_query = f"SELECT household_id FROM household WHERE household_id = {household_id}"
    result = execute_query(db_query)
    if not result:
        return False
    else:
        return True
    
def generate_porch_id():
    db_query = "SELECT MAX(id) FROM porch_contents"
    result = execute_query(db_query)
    max_id = 1
    if result:
        max_id  = result[0][0] 
    return max_id  + 1

def scrub_tool_values(text):
    keywords = ["household_id", "household", "item_id", "item", "id"]
    words = text.split()
    result = []

    i = 0
    while i < len(words):
        word = words[i].lower()

        # Match 
        if word in keywords:
            result.append(f"{word}: ___")
            i += 1
            # Skip next word if it's a number
            if i < len(words) and words[i].isdigit():
                i += 1
        elif words[i].isdigit():
            result.append("___")
            i += 1
        else:
            result.append(words[i])
            i += 1

    return " ".join(result)
from typing import Dict, List
from pydantic import BaseModel
from pydantic_ai import Tool, RunContext
from execute_query import execute_query
from helpers import item_id_check, household_id_check, generate_porch_id
from state import state as fido_state


def search_household_items(ctx: RunContext, household_id: int) -> List[Dict]:
    db_query = f"""
                SELECT i.name, i.details, s.status, p.id
                FROM porch_contents AS p
                JOIN item_list AS i ON p.item_id = i.item_id
                JOIN status AS s ON p.status_id = s.status_id
                WHERE p.household_id = {household_id};
                """
    rows = execute_query(db_query)
    if not rows:
        return []
    return [
        {"item": row[0], "description": row[1], "status": row[2], "item_id": row[3]}
        for row in rows
    ]

search_household_items_tool = Tool(search_household_items)

def search_for_item (ctx: RunContext, id: int):
    db_query = f"""
                SELECT i.name, i.details, s.status, p.id
                FROM porch_contents AS p
                JOIN item_list AS i ON p.item_id = i.item_id
                JOIN status AS s ON p.status_id = s.status_id
                WHERE p.id = {id};
                """
    rows = execute_query(db_query)
    if not rows:
        return []
    return [
        {"item": row[0], "description": row[1], "status": row[2], "item_id": row[3]}
        for row in rows
    ]

search_for_item_tool = Tool(search_for_item)

def chew_item(ctx: RunContext, id):
    if not item_id_check(id):
        return {"Nothing found"}
    db_query = f"UPDATE porch_contents SET status_id = 2 WHERE id = {id}"
    execute_query(db_query, True)
    return {"Item chewed"}

chew_item_tool = Tool(chew_item)

def eat_item (ctx: RunContext, id):
    if not item_id_check(id):
        return {"Nothing found"}
    db_query = f"DELETE FROM porch_contents WHERE id = {id}"
    execute_query(db_query, True)
    return {"Item eaten"}

eat_item_tool = Tool(eat_item)

def place_item(ctx: RunContext, household_id: int, name: str):
    if not household_id_check(household_id):
        return {"Household not found"}
    item_query = f"SELECT item_id FROM item_list WHERE name ILIKE '%{name}%';"
    result = execute_query(item_query)
    if not result:
        return {"Item not found in item list"}
    item_id = result[0][0]
    porch_id = generate_porch_id()
    insert_query = f"""
        INSERT INTO porch_contents (id, item_id, status_id, household_id)
        VALUES ({porch_id}, {item_id}, 1, {household_id});
    """
    execute_query(insert_query, commit=True)
    return {f"{name} added to porch at household {household_id} (porch ID {porch_id})"}

place_item_tool = Tool(place_item)

def naughty_boy(ctx: RunContext):
    fido_state.is_naughty = True
    return {"Fido is now naughty!"}

naughty_boy_tool = Tool(naughty_boy)

def happy_boy(ctx: RunContext):
    fido_state.is_naughty = False
    return {"Fido is now happy!"}

happy_boy_tool = Tool(happy_boy)

def total_destruction_cost(ctx: RunContext) -> List[Dict]:
    db_query = f"""
                SELECT SUM(il.cost)
                FROM porch_contents AS p 
                JOIN item_list AS il ON p.item_id = il.item_id
                WHERE p.status_id = 2;
                """
    rows = execute_query(db_query)

    if not rows or rows[0][0] is None:
        return [{"total_cost": "$0.00"}]

    total = round(rows[0][0], 2)
    return [{"total_cost": f"${total:.2f}"}]

total_destruction_cost_tool = Tool(total_destruction_cost)
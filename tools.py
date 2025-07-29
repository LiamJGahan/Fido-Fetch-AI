from typing import Dict, List
from pydantic import BaseModel
from execute_query import execute_query
from helpers import item_id_check, household_id_check, generate_porch_id


def search_household_items(household_id: int) -> List[Dict]:
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

def search_for_item (id: int):
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

def chew_item(id):
    if not item_id_check(id):
        return {"Nothing found"}
    db_query = f"UPDATE porch_contents SET status_id = 2 WHERE id = {id}"
    execute_query(db_query, True)
    return {"Item chewed"}

def eat_item (id):
    if not item_id_check(id):
        return {"Nothing found"}
    db_query = f"DELETE FROM porch_contents WHERE id = {id}"
    execute_query(db_query, True)
    return {"Item eaten"}

def place_item(household_id: int, name: str):
    if not household_id_check(household_id):
        return {"Household not found"}
    db_query = f"SELECT item_id FROM item_list WHERE name ilike '%{name}%';"
    execute_query(db_query)
    item_id = db_query
    if not item_id:
        return {"Item not found in item list"}
    id_no = generate_porch_id()
    db_query = f"""
                INSERT INTO porch_contents (id, item_id, status_id, household_id)
                VALUES ({id_no}, {item_id}, {1}, {household_id})
                """
    return {f"{name} added to porch at {household_id}"}

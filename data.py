from sqlite3 import *
import json

def open_connection() -> tuple[Connection, Cursor]:
    con = connect("questions.db")
    return con, con.cursor()

def close_connection(con: Connection):
    con.close()

def create_table():
    con, cur = open_connection()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS question (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            incorrect_answers TEXT NOT NULL,
            game TEXT NOT NULL,
            img TEXT NOT NULL,
            UNIQUE(game, text)
        );
    """)
    close_connection(con)

def add_question(question_obj: tuple) -> bool:
    con, cur = open_connection()
    if len(question_obj) != 5:
        close_connection(con)
        return False
    if not isinstance(question_obj[0], str):
        close_connection(con)
        return False
    if not isinstance(question_obj[1], str):
        close_connection(con)
        return False
    if not isinstance(question_obj[2], list) or len(question_obj[2]) != 3:
        close_connection(con)
        return False
    if not isinstance(question_obj[3], str):
        close_connection(con)
        return False
    if not isinstance(question_obj[4], str):
        close_connection(con)
        return False
    try:
        cur.execute(
            """INSERT INTO question
            (text, correct_answer, incorrect_answers, game, img)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(game, text) DO NOTHING""",
            (
                question_obj[0],
                question_obj[1],
                json.dumps(question_obj[2]),
                question_obj[3],
                question_obj[4],
            ),)
        con.commit()
        inserted = cur.rowcount == 1
    finally:
        close_connection(con)
    return inserted

def give_questions() -> list[dict[str, str | list[str]]]:
    con, cur = open_connection()
    try:
        cur.execute("""
            SELECT id, text, correct_answer, incorrect_answers, game, img
            FROM question
            ORDER BY id
        """)

        return [
            {
                "id": question_id,
                "question": text,
                "correct_answer": correct_answer,
                "incorrect_answers": json.loads(incorrect_answers),
                "game": game,
                "img": img
            }
            for question_id, text, correct_answer, incorrect_answers, game, img in cur.fetchall()
        ]
    finally:
        close_connection(con)

def get_question(id: int) -> dict | None:
    con, cur = open_connection()
    try:
        cur.execute("""
            SELECT id, text, correct_answer, incorrect_answers, game, img
            FROM question
            WHERE id = ?
        """, (id,))
        row = cur.fetchone()
        if row is None:
            return None
        question_id, text, correct_answer, incorrect_answers, game, img = row
        return {"id": question_id,
                "question": text,
                "correct_answer": correct_answer,
                "incorrect_answers": json.loads(incorrect_answers),
                "game": game,
                "img": img}
    finally:
        close_connection(con)

def delete_question(id: int) -> bool:
    con, cur = open_connection()
    try: 
        cur.execute("DELETE FROM question WHERE id = ?", (id,))
        con.commit()
        return cur.rowcount > 0
    finally:
        close_connection(con)

def replace_question(id: int, obj: tuple) -> bool:
    con, cur = open_connection()
    try:
        cur.execute("""
            UPDATE question
            SET text = ?,
                correct_answer = ?,
                incorrect_answers = ?,
                game = ?,
                img = ?
            WHERE id = ?
        """, (
            obj[0],
            obj[1],
            json.dumps(obj[2]),
            obj[3],
            obj[4],
            id,
        ))
        con.commit()
        return cur.rowcount > 0
    finally:
        close_connection(con)
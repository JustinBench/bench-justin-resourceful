from sqlite3 import *
import json

def open_connection() -> tuple[Connection, Cursor]:
    con = connect("questions.db")
    return con, con.cursor()

def close_connection(con: Connection):
    con.close()

#When receiving a tuple ("question-text", "correct-answer", "incorrect-answer", "game", "img-file"):
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
            SELECT text, correct_answer, incorrect_answers, game, img
            FROM question
            ORDER BY game
        """)

        return [
            {
                "question": text,
                "correct_answer": correct_answer,
                "incorrect_answers": json.loads(incorrect_answers),
                "game": game,
                "img": img
            }
            for text, correct_answer, incorrect_answers, game, img in cur.fetchall()
        ]
    finally:
        close_connection(con)

def list_questions() -> list[str]:
    questions = []
    con, cur = open_connection()
    for row in cur.execute("SELECT text FROM question ORDER BY game"):
        questions.append(row[0])
        print(row[0])
    close_connection(con)
    return questions
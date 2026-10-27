from sqlite3 import *
import json
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "questions.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

class DataBase:
    def __init__(self):
        self.con: Connection = None
        self.cur: Cursor = None

    def open_connection(self) -> tuple[Connection, Cursor]:
        self.con = connect(str(DATABASE_PATH))
        self.cur = self.con.cursor()

    def close_connection(self) -> None:
        if self.con is not None:
            self.con.close()
        self.__init__()

    def create_table(self):
        self.open_connection()
        try:
            schema = SCHEMA_PATH.read_text(encode="utf-8")
            self.con.executescript(schema)
            self.con.commit()
        finally:
            self.close_connection()

    def add_question(self, question_obj: tuple) -> bool:
        self.open_connection()
        if len(question_obj) != 5:
            self.close_connection()
            return False
        if not isinstance(question_obj[0], str):
            self.close_connection()
            return False
        if not isinstance(question_obj[1], str):
            self.close_connection()
            return False
        if not isinstance(question_obj[2], list) or len(question_obj[2]) != 3:
            self.close_connection()
            return False
        if not isinstance(question_obj[3], str):
            self.close_connection()
            return False
        if not isinstance(question_obj[4], str):
            self.close_connection()
            return False
        try:
            self.cur.execute(
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
            self.con.commit()
            inserted = self.cur.rowcount == 1
        finally:
            self.close_connection()
        return inserted

    def give_questions(self) -> list[dict[str, str | list[str]]]:
        self.open_connection()
        try:
            self.cur.execute("""
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
                for question_id, text, correct_answer, incorrect_answers, game, img in self.cur.fetchall()
            ]
        finally:
            self.close_connection()

    def get_question(self, id: int) -> dict | None:
        self.open_connection()
        try:
            self.cur.execute("""
                SELECT id, text, correct_answer, incorrect_answers, game, img
                FROM question
                WHERE id = ?
            """, (id,))
            row = self.cur.fetchone()
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
            self.close_connection()

    def delete_question(self, id: int) -> bool:
        self.open_connection()
        try: 
            self.cur.execute("DELETE FROM question WHERE id = ?", (id,))
            self.con.commit()
            return self.cur.rowcount > 0
        finally:
            self.close_connection()

    def replace_question(self, id: int, obj: tuple) -> bool:
        self.open_connection()
        try:
            self.cur.execute("""
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
            self.con.commit()
            return self.cur.rowcount > 0
        finally:
            self.close_connection()

import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://opentdb.com"])

MESSAGE_FILE = Path(__file__).parent / "messages.jsonl"

@app.route("/")
def main():
    return render_template("main/index.html")

@app.route("/quiz/add_questions")
def add_question():
    return render_template("main/add_question.html")

@app.route("/quiz/take_quiz")
def take_quiz():
    return render_template("main/quiz.html")

@app.route("/messages", methods=["GET"])
def get_questions():
    questions = []

    with MESSAGE_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                questions.append(json.loads(line))

    return jsonify(questions), 200

@app.route("/messages", methods=["POST"])
def post_new_question():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain a JSON object"
        }), 400

    question = data.get("question")
    correct_answer = data.get("correct_answer")
    incorrect_answers = data.get("incorrect_answers")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "The question field must contain text"
        }), 400

    if not isinstance(correct_answer, str) or not correct_answer.strip():
        return jsonify({
                    "error": "There must be a correct answer that contains text"
                }), 400

    if len(incorrect_answers) == 0:
        return jsonify({
                    "error": "There must be at least one incorrect answer"
                })
    else:
        for answer in incorrect_answers:
            if not isinstance(answer, str) or len(answer) == 0:
                return jsonify({
                            "error": "Incorrect answers should be strings and should not be empty"
                        })

    new_question = {
        "question": question.strip(),
        "correct_answer": data.get("correct_answer"),
        "incorrect_answers": data.get("incorrect_answers")
    }

    with MESSAGE_FILE.open("a+", encoding="utf-8") as file:
        file.seek(0, 2)

        if file.tell() > 0:
            file.seek(file.tell() - 1)
            last_character = file.read(1)

            if last_character != "\n":
                file.write("\n")

        file.write(json.dumps(new_question) + "\n")

    return "", 201

@app.route("/about_me")
def project_one():
    return render_template("project_one/about_me.html")

@app.route("/original")
def project_two():
    return render_template("project_two/zelda.html")

if __name__ == "__main__":
    app.run()
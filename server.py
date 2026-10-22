import json
import uuid
import data
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

app = Flask(__name__)
MAX_IMAGE_SIZE = 5 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_SIZE + 64 * 1024
CORS(app, origins=["https://opentdb.com"])

MEDIA_DIRECTORY = Path(__file__).parent / "static" / "media"


def image_extension(contents):
    if contents.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if contents.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if contents.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if contents.startswith(b"RIFF") and contents[8:12] == b"WEBP":
        return ".webp"
    return None


@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(error):
    return jsonify({"error": "Uploaded files must be 5 MB or smaller"}), 413

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/quiz/add_questions")
def add_question():
    return render_template("add_question.html")

@app.route("/quiz/take_quiz")
def take_quiz():
    return render_template("quiz.html")

@app.route("/messages", methods=["GET"])
def get_questions():
    questions = data.give_questions()
    return jsonify(questions), 200

@app.route("/messages", methods=["POST"])
def post_new_question():
    if request.is_json:
        payload = request.get_json(silent=True)
        uploaded_image = None
    elif request.mimetype == "multipart/form-data":
        payload = request.form
        uploaded_image = request.files.get("image")
    else:
        return jsonify({
            "error": "Content-Type must be application/json or multipart/form-data"
        }), 400

    if not payload or (request.is_json and not isinstance(payload, dict)):
        return jsonify({
            "error": "Request body must contain question data"
        }), 400

    question = payload.get("question")
    correct_answer = payload.get("correct_answer")
    if request.is_json:
        incorrect_answers = payload.get("incorrect_answers")
    else:
        incorrect_answers = request.form.getlist("incorrect_answers")
    game = payload.get("game")
    image = payload.get("img", "hestus_gift.png")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "The question field must contain text"
        }), 400

    if not isinstance(game, str) or not game.strip():
        return jsonify({
            "error": "The game field must contain text"
        }), 400

    if not isinstance(correct_answer, str) or not correct_answer.strip():
        return jsonify({
            "error": "There must be a correct answer that contains text"
        }), 400

    if not isinstance(incorrect_answers, list) or not incorrect_answers:
        return jsonify({
            "error": "There must be at least one incorrect answer"
        }), 400

    if len(incorrect_answers) != 3:
        return jsonify({
                    "error": "There should be three incorrect answers"
                }), 400
    for answer in incorrect_answers:
        if not isinstance(answer, str) or not answer.strip():
            return jsonify({
                "error": "Incorrect answers should be strings and should not be empty"
            }), 400

    image_contents = None
    if uploaded_image and uploaded_image.filename:
        image_contents = uploaded_image.read()
        if len(image_contents) > MAX_IMAGE_SIZE:
            return jsonify({
                "error": "Uploaded files must be 5 MB or smaller"
            }), 413

        extension = image_extension(image_contents)
        if extension is None:
            return jsonify({
                "error": "Upload a valid PNG, JPEG, GIF, or WebP image"
            }), 400

        original_stem = secure_filename(Path(uploaded_image.filename).stem) or "question-image"
        image = f"{uuid.uuid4().hex}_{original_stem}{extension}"
    elif not isinstance(image, str) or not image.strip():
        return jsonify({
            "error": "The img field must contain an image key"
        }), 400

    new_question = (
        question.strip(),
        correct_answer.strip(),
        incorrect_answers,
        game.strip(),
        image.strip() if isinstance(image, str) else image
    )

    if image_contents is not None:
        MEDIA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        (MEDIA_DIRECTORY / new_question[4]).write_bytes(image_contents)

    if data.add_question(new_question):
        return "", 201
    else:
        return jsonify({"error": "Could not save question"}), 500

if __name__ == "__main__":
    app.run()
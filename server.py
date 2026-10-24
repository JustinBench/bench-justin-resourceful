import json, re, uuid, sqlite3
from data import DataBase
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

app = Flask(__name__)
db = DataBase()
db.create_table()
MAX_IMAGE_SIZE = 5 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_SIZE + 64 * 1024
CORS(
    app,
    origins="*",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
    supports_credentials=False,
)

MEDIA_DIRECTORY = Path(__file__).resolve().parent / "static" / "media"


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

def delete_uploaded_image(image_name):
    """Remove an app-uploaded image, never a bundled/default image."""
    if not isinstance(image_name, str) or not image_name:
        return

    # Uploaded names are generated as 32 hex characters, an underscore,
    # a sanitized stem, and a supported extension. Bundled images don't
    # use this naming format.
    if not re.fullmatch(r"[0-9a-f]{32}_.+\.(png|jpg|gif|webp)", image_name, re.IGNORECASE):
        return

    media_root = MEDIA_DIRECTORY.resolve()
    image_path = (MEDIA_DIRECTORY / image_name).resolve()
    if image_path.parent != media_root:
        return

    image_path.unlink(missing_ok=True)

@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(error):
    return jsonify({"error": "Uploaded files must be 5 MB or smaller"}), 413

@app.errorhandler(404)
def handle_not_found(error):
    if request.path.startswith("/questions_and_answers"):
        return jsonify({"error": "API route or question not found"}), 404
    return error

@app.errorhandler(405)
def handle_method_not_allowed(error):
    if request.path.startswith("/questions_and_answers"):
        return jsonify({"error": "Method not allowed for this API route"}), 405
    return error

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/add_questions")
def add_question():
    return render_template("add_question.html")

@app.route("/take_quiz")
def take_quiz():
    return render_template("quiz.html")

@app.route("/view_questions")
def review():
    return render_template("questions.html")

@app.route("/questions_and_answers", methods=["GET"])
def get_questions_and_answers():
    questions = db.give_questions()
    return jsonify(questions), 200

@app.route("/questions_and_answers/<int:question_id>", methods=["GET"])
def get_quiz_question(question_id):
    question = db.get_question(question_id)
    if question is None:
        return jsonify({"error": f"No question found with ID {question_id}"}), 404
    return jsonify(question), 200

@app.route("/questions_and_answers/<int:question_id>", methods=["DELETE"])
def delete_quiz_question(question_id):
    existing = db.get_question(question_id)
    if existing is None:
        return jsonify({"error": f"No question found with ID {question_id}"}), 404

    deleted = db.delete_question(question_id)
    if not deleted:
        return jsonify({"error": f"No question found with ID {question_id}"}), 404
    delete_uploaded_image(existing["img"])
    return "", 204

@app.route("/questions_and_answers/<int:question_id>", methods=["PUT"])
def replace_question(question_id):
    existing = db.get_question(question_id)
    if existing is None:
        return jsonify({"error": "Question not found"}), 404
    question = request.form.get("question", "").strip()
    correct_answer = request.form.get("correct_answer", "").strip()
    incorrect_answers = [answer.strip() for answer in request.form.getlist("incorrect_answers")]
    game = request.form.get("game", "").strip()
    image = request.form.get("img", existing["img"])

    if any(not answer for answer in incorrect_answers):
        return jsonify({
            "error": "Incorrect answers must not be empty"
        }), 400

    uploaded_image = request.files.get("image")
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
    if not question or not correct_answer or not game or len(incorrect_answers) != 3:
        return jsonify({"error": "All question fields are required"}), 400

    if image_contents is not None:
        MEDIA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        (MEDIA_DIRECTORY / image).write_bytes(image_contents)

    question_obj = (question, correct_answer, incorrect_answers, game, image)
    try:
        replaced = db.replace_question(question_id, question_obj)
    except sqlite3.IntegrityError:
        if image_contents is not None:
            delete_uploaded_image(image)
        return jsonify({
            "error": "A question with this text already exists for that game"
        }), 409
    except Exception:
        if image_contents is not None:
            delete_uploaded_image(image)
        raise

    if not replaced:
        if image_contents is not None:
            delete_uploaded_image(image)
        return jsonify({"error": "Question not found"}), 404

    if image_contents is not None and image != existing["img"]:
        delete_uploaded_image(existing["img"])
    return "", 204

@app.route("/questions_and_answers", methods=["POST"])
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

    if db.add_question(new_question):
        return "", 201

    if image_contents is not None:
        delete_uploaded_image(new_question[4])

    return jsonify({"error": "A question with this text already exists for that game"}), 409

if __name__ == "__main__":
    app.run()

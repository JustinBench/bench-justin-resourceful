# Zelda Trivia Question API

A small Flask application for a Zelda trivia quiz. Questions are stored in SQLite, and the browser uses the API to list questions, retrieve individual questions, add questions, replace them, and delete them. Uploaded question images are saved under `static/media/`.

## Resource

The resource is a **Question**. Its database-generated identifier is `id`. Its five data attributes are:

| Attribute | Meaning |
| --- | --- |
| `text` | The question text (returned by the API as `question`) |
| `correct_answer` | The correct answer |
| `incorrect_answers` | A JSON array containing three incorrect answers |
| `game` | The Zelda game or category |
| `img` | The image filename associated with the question |

The database enforces uniqueness on `(game, text)`. SQLite generates the integer `id`; clients do not provide or change it.

## Database schema

```sql
CREATE TABLE question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    incorrect_answers TEXT NOT NULL,
    game TEXT NOT NULL,
    img TEXT NOT NULL,
    UNIQUE(game, text)
);
```

`DataBase` in `data.py` encapsulates the SQLite operations. The table is created when the Flask application starts. The database file is located next to `data.py`, so starting the server from another working directory still uses the project’s `questions.db`.

## REST API

The collection path is `/questions_and_answers`. The item path is `/questions_and_answers/<question_id>`, where `question_id` is the integer ID assigned by SQLite.

| Operation | Method and path | Behavior and responses |
| --- | --- | --- |
| List | `GET /questions_and_answers` | Returns the question collection as JSON (`200`). |
| Retrieve | `GET /questions_and_answers/<question_id>` | Returns one question as JSON (`200`), or an error JSON response if the ID does not exist (`404`). |
| Create | `POST /questions_and_answers` | Creates a question from JSON or multipart form data (`201`). Invalid fields or unsupported content type return an error (`400`); oversized image uploads return `413`. |
| Replace | `PUT /questions_and_answers/<question_id>` | Replaces all editable question attributes from multipart form data (`204`). The existing `id` is unchanged. The current image is retained if no new image is uploaded. Missing IDs return `404`; invalid fields return `400`; oversized image uploads return `413`. |
| Delete | `DELETE /questions_and_answers/<question_id>` | Deletes the question and its app-uploaded image (`204`), or returns an error if the ID does not exist (`404`). |

Create and replace accept three repeated `incorrect_answers` form fields. An optional uploaded image is sent in the `image` field. The `img` field contains the current image filename during replacement so it can be retained when no new file is selected.

Requests that violate the database's `(game, text)` uniqueness constraint return `409 Conflict` with a JSON error message. Invalid or missing fields and invalid image formats return `400`; uploaded images larger than 5 MB return `413`. Requests for a missing question or an unrecognized path under the API prefix return `404`, and unsupported methods on API routes return `405`. These API errors use JSON responses with an `error` field. Unexpected server errors remain server-side failures (`500`) and should be diagnosed from the server log.

The quiz chooses random IDs from the list response, then retrieves each selected question through the item endpoint. The review page uses the same API to populate its list and sends Ajax requests for edits and deletes.

### Browser page routes

These routes serve HTML pages and are separate from the JSON API:

| Path | Page |
| --- | --- |
| `/` | Home page |
| `/take_quiz` | Quiz |
| `/add_questions` | Add-question form |
| `/view_questions` | Question review and editing page |

## CORS

Flask-CORS is configured on the Flask app for browser clients. It allows the API’s HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, and `OPTIONS`) and the `Content-Type` request header. Flask/Flask-CORS supplies the preflight response for cross-origin requests. Credentials such as cross-origin cookies are not enabled.

The current configuration allows all origins for this assignment because a separate deployed client origin has not been specified. This is appropriate for an uncredentialed class demonstration, but a deployed API should replace the wildcard with the exact origin(s) of its client, including scheme and port. CORS controls whether browser JavaScript can read cross-origin responses; it is not authentication or access control.

## Run on another machine

### Requirements

- Python 3.10 or newer
- `pip` and Python's built-in `venv` module
- A writable copy of this project directory

SQLite is included with Python. No Node.js, external database server, or separate image service is required.

### Windows PowerShell

From the project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py
```

### macOS, Linux, or WSL

From the project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
```

Open `http://127.0.0.1:5000/` in a browser. Keep the server running while using the site. The project directory must be writable because the application creates or updates `questions.db` and stores uploaded images in `static/media/`. If `questions.db` is absent, the app creates an empty database and initializes the table on startup.

## Project files

- `server.py` — Flask pages, API routes, request validation, CORS, and image upload handling.
- `data.py` — `DataBase` class and SQLite schema/CRUD operations.
- `questions.db` — SQLite database containing the current question collection.
- `templates/` — HTML pages rendered by Flask.
- `static/script.js` — quiz, review, add, replace, and delete client behavior.
- `static/style.css` — page and component styling.
- `static/media/` — bundled and uploaded question images.
- `requirements.txt` — Python package dependencies.
- `schema.sql` — SQLite table schema.

# Notes

Relational Databases have tables with attributes that may relate to each other. Perhaps the "game" field was a expanded to a new table, where every game instance had the title of the game, the dungeons in the game, the items in the game, the final boss, etc. Then the "game" field in the quesiton instance would relate to the game in the game table.

This assignment uses SQL but doesn't really need to since it's just one table. Key-value stores, like dictionaries, are non-relational.

CSS and SQL are similar languages in that the process or desired outcome is described rather than actually written out. You tell CSS what properties you want applied to what elements, and you tell SQL what objects you want based on what fields meet certain criteria or whatever. You don't actually have to write out procedures with for loops and if statements.
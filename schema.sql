CREATE TABLE IF NOT EXISTS question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    incorrect_answers TEXT NOT NULL,
    game TEXT NOT NULL,
    img TEXT NOT NULL,
    UNIQUE(game, text)
);
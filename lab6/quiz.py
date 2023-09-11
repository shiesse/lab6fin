import sqlite3

# Создание базы данных и подключение
db = sqlite3.connect('quiz.db')
cursor = db.cursor()

# Создание таблиц
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE quizzes (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        user_id INTEGER REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE questions (
        id INTEGER PRIMARY KEY,
        quiz_id INTEGER REFERENCES quizzes(id),
        question TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE answers (
        id INTEGER PRIMARY KEY,
        question_id INTEGER REFERENCES questions(id),
        answer TEXT NOT NULL,
        is_correct INTEGER NOT NULL
    )
''')

db.commit()
db.close()

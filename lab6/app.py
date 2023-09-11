from flask import Flask, render_template, request, g, redirect
import sqlite3


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Главная страница с отображением тестов и кнопкой создания теста
@app.route('/', methods=['GET'])
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM quizzes")
    quizzes = cursor.fetchall()
    db.close()
    return render_template('index.html', quizzes=quizzes)

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect('quiz.db')
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


#страница создания теста, добавления вопросов и ответов к ним.
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        title = request.form['title']
        description = request.form['description']

        cursor.execute('INSERT INTO quizzes (title, description) VALUES (?, ?)', (title, description))
        quiz_id = cursor.lastrowid

        for field in request.form:
            if field.startswith('question_'):
                question_text = request.form[field]
                cursor.execute('INSERT INTO questions (quiz_id, question) VALUES (?, ?)', (quiz_id, question_text))
                question_id = cursor.lastrowid

                question_number = field.split('_')[1]
                answer_number = 1
                while True:
                    answer_text = request.form.get(f'answer_{question_number}_{answer_number}')
                    if answer_text:
                        is_correct = 1 if request.form.get(f'correct_{question_number}_{answer_number}') else 0
                        cursor.execute('INSERT INTO answers (question_id, answer, is_correct) VALUES (?, ?, ?)',
                                       (question_id, answer_text, is_correct))
                        answer_number += 1
                    else:
                        break

        db.commit()
        db.close()
        return redirect('/')

    return render_template('create_quiz.html')



#страница прохождения теста
@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    if request.method == 'POST':
        return redirect(f'/quiz_results/{quiz_id}', code=302)

    connection = sqlite3.connect('quiz.db')
    cursor = connection.cursor()

    # Получение данных о тесте
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()

    # Получение вопросов и вариантов ответов для теста
    cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()

    cursor.execute("SELECT * FROM answers WHERE question_id IN (SELECT id FROM questions WHERE quiz_id = ?)", (quiz_id,))
    answers = cursor.fetchall()

    connection.close()

    return render_template('take_quiz.html', quiz=quiz, questions=questions, answers=answers)
#страница результатов пройденного теста
@app.route('/quiz_results/<int:quiz_id>', methods=['POST'])
def quiz_results(quiz_id):
    connection = sqlite3.connect('quiz.db')
    cursor = connection.cursor()

    # Получение всех вопросов для данного теста
    cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()

    score = 0

    for question in questions:
        answer_key = f"answer_{question[0]}"
        selected_answer_id_str = request.form.get(answer_key)

        if selected_answer_id_str is not None:
            selected_answer_id = int(selected_answer_id_str)
            
            # Получение правильного ответа для вопроса
            cursor.execute("SELECT id FROM answers WHERE question_id = ? AND is_correct = 1", (question[0],))
            correct_answer_id = cursor.fetchone()[0]

            if selected_answer_id == correct_answer_id:
                score += 1

    connection.close()

    total_questions = len(questions)

    return render_template('quiz_results.html', score=score, total_questions=total_questions)



if __name__ == '__main__':
    app.run(debug=True)

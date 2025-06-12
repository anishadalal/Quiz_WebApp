from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, json
from models import init_db

app = Flask(__name__)
app.secret_key = 'secret'
init_db()

def get_db():
    return sqlite3.connect('quiz.db')

@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html', name=session['user'])
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            db = get_db()
            db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            db.commit()
            return redirect('/login')
        except:
            return "User already exists!"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        if user:
            session['user'] = user[1]
            session['user_id'] = user[0]
            return redirect('/')
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/select_subject', methods=['GET', 'POST'])
def select_subject():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        subject = request.form['subject']
        difficulty = request.form['difficulty']
        return redirect(url_for('quiz', subject=subject, difficulty=difficulty))
    return render_template('select_subject.html')



# @app.route('/quiz', methods=['GET', 'POST'])
# def quiz():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     # Handle quiz submission
#     if request.method == 'POST':
#         subject = session.get('selected_subject')
#         difficulty = session.get('selected_difficulty')

#         with open('questions.json') as f:
#             all_questions = json.load(f)

#         questions = all_questions.get(subject, {}).get(difficulty, [])

#         score = 0
#         for i, q in enumerate(questions):
#             user_answer = request.form.get(f'q{i}')
#             if user_answer == q['answer']:
#                 score += 1

#         # Save history to DB
#         conn = sqlite3.connect('quiz.db')
#         c = conn.cursor()
#         c.execute("INSERT INTO history (user_id, subject, difficulty, score, total) VALUES (?, ?, ?, ?, ?)",
#                   (session['user_id'], subject, difficulty, score, len(questions)))
#         conn.commit()
#         conn.close()

#         return render_template('result.html', score=score, total=len(questions))

#     # GET method → show quiz
#     subject = request.args.get('subject')
#     difficulty = request.args.get('difficulty')

#     # Save selection in session for POST use
#     session['selected_subject'] = subject
#     session['selected_difficulty'] = difficulty

#     with open('questions.json') as f:
#         all_questions = json.load(f)

#     questions = all_questions.get(subject, {}).get(difficulty, [])

#     # ✅ Debug prints
#     print("Subject:", subject)
#     print("Difficulty:", difficulty)
#     print("Questions:", questions)

#     if not questions:
#         return "⚠️ No questions found for this subject and difficulty level."

#     return render_template('quiz.html', questions=questions, subject=subject, difficulty=difficulty)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Handle quiz submission
    if request.method == 'POST':
        subject = session.get('selected_subject')
        difficulty = session.get('selected_difficulty')

        with open('questions.json') as f:
            all_questions = json.load(f)

        questions = all_questions.get(subject, {}).get(difficulty, [])

        # Add unique ID for each question
        for i, q in enumerate(questions):
            q['id'] = f'q{i}'

        score = 0
        for q in questions:
            user_answer = request.form.get(q['id'])
            if user_answer == q['answer']:
                score += 1

        # Save history to DB
        conn = sqlite3.connect('quiz.db')
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, subject, difficulty, score, total) VALUES (?, ?, ?, ?, ?)",
                  (session['user_id'], subject, difficulty, score, len(questions)))
        conn.commit()
        conn.close()

        return render_template('result.html', score=score, total=len(questions))

    # GET method → show quiz
    subject = request.args.get('subject')
    difficulty = request.args.get('difficulty')

    session['selected_subject'] = subject
    session['selected_difficulty'] = difficulty

    with open('questions.json') as f:
        all_questions = json.load(f)

    questions = all_questions.get(subject, {}).get(difficulty, [])

    # ✅ Add unique ID here too for the GET route
    for i, q in enumerate(questions):
        q['id'] = f'q{i}'

    if not questions:
        return "⚠️ No questions found for this subject and difficulty level."

    return render_template('quiz.html', questions=questions, subject=subject, difficulty=difficulty)




@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')
    db = get_db()
    cur = db.execute("SELECT subject, difficulty, score, total, timestamp FROM history WHERE user_id=?", (session['user_id'],))
    history = cur.fetchall()
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)

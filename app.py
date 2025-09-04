from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai

app = Flask(__name__)

#Konfiguracja Gemini API
genai.configure(api_key="AIzaSyDueZqXZfCV6OKBmD9gKZ8OZADwHFT_PNQ")
model = genai.GenerativeModel("gemini-1.5-flash")
rule = """You have to answer only using TRUE if answer is up to 90% true, FALSE if answer is mostly false, FINE if answer is slightly wrong."""

#Konfiguracja SQL
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    fake_answer = db.Column(db.Text)
    second_fake_answer = db.Column(db.Text)

    def __init__(self, question, answer="", fake_answer="", second_fake_answer=""):
        self.question = question
        self.answer = answer
        self.fake_answer = fake_answer
        self.second_fake_answer = second_fake_answer


with app.app_context():
    db.create_all()
    if Question.query.count() == 0:
        q1 = Question("What does NLP stand for?")
        q2 = Question("Which task is an example of NLP?", "Machine translation", "Image classification", "Sorting numbers")
        q3 = Question("Which library is commonly used for NLP in Python?", "NLTK", "NumPy", "Matplotlib")
        q4 = Question("Write one example of a real-world application of NLP:")
        q5 = Question("Which task involves assigning categories to text?", "Text classification", "Clustering", "Image segmentation")
        q6 = Question("Name one transformer-based model used in NLP:")

        db.session.add_all([q1, q2, q3, q4, q5, q6])
        db.session.commit()

import random

@app.route('/', methods=['GET', 'POST'])
def main():
    questions = Question.query.all()
    quiz = []
    for q in questions:
        if not q.answer:
            quiz.append({
                "id": q.id,
                "question": q.question
            })
        else:
            options = [{"text": q.answer, "correct": True},{"text": q.fake_answer, "correct": False},{"text": q.second_fake_answer, "correct": False}]
            random.shuffle(options)
            quiz.append({
                "id": q.id,
                "question": q.question,
                "options": options
            })

    if request.method == "POST":
        answers = {}
        for key, value in request.form.items():
            if key.startswith("answer_"):
                answers[key] = value
        print(answers)

    return render_template("app.html", quiz=quiz)



def open_answer(input):
    response = model.generate_content(rule + input)
    response_text = response.text
    return response_text

if __name__ == '__main__':
    app.run(debug=True)

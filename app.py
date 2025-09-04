from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import random
app = Flask(__name__)

#Konfiguracja Gemini API
genai.configure(api_key="AIzaSyCjwFhiMU8NzjqzcsGaM5ipfB85gamSCGk")
model = genai.GenerativeModel("gemini-1.5-flash")
rule = """You have to answer only using number 1 if answer is up to 90% true, 0 if answer is mostly false or empty, 0.5 if answer is slightly wrong. Only answers are: 1,0,0.5 ! """

#Konfiguracja SQL
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    best_score = db.Column(db.Float)

    def __init__(self, best_score=None):
        self.best_score = best_score

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    fake_answer = db.Column(db.Text)
    second_fake_answer = db.Column(db.Text)

    def __init__(self, question, answer=None, fake_answer=None, second_fake_answer=None):
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
        user1 = User(None)

        db.session.add_all([q1, q2, q3, q4, q5, user1])
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def main():
    points = None
    user1 = User.query.first()
    questions = Question.query.all()
    quiz = []
    for q in questions:
        if not q.answer:
            quiz.append({
                "id": q.id,
                "question": q.question
            })
        else:
            options = [{"text" : q.answer},{"text" : q.fake_answer},{"text" : q.second_fake_answer}]
            random.shuffle(options)
            quiz.append({
                "id": q.id,
                "question": q.question,
                "options": options
            })

    if request.method == "POST":
        points = 0.0
        for q in questions:
            user_answer = (request.form.get(str(q.id)))
            print(user_answer)
            if not q.answer:
                #Zabezpieczenie przed przeciążeniem Gemini API
                if user_answer == "":
                    pass
                else:
                    points += open_answer(f"{q.question} User answer: {user_answer}")
            else:
                if q.answer == user_answer:
                    points += 1
                else:
                    pass
        if user1.best_score < points:
            user1.best_score = points
            db.session.commit()

    return render_template("app.html", quiz=quiz, points=points, best_score=user1.best_score)

def open_answer(input):
    print(input)
    response = model.generate_content(rule + input)
    points = float(response.text)
    return points

if __name__ == '__main__':
    app.run(debug=True)
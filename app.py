from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import *
from database import create_tables_if_not_exist
import json
import os

app = Flask(__name__)

# Загрузка конфигурации из файла
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Настройка подключения к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".format(
    **config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация экземпляра SQLAlchemy
db.init_app(app)

# Создание таблиц, если они не существуют
if not os.path.exists("config/initialized"):
    with app.app_context():
        create_tables_if_not_exist()
        open("config/initialized", "w").close()


# Главная страница
@app.route("/")
def base():
    return render_template("base.html")


# Страница с тестами
@app.route("/tests")
def tests():
    return render_template("tests.html")


@app.route("/question", methods=["GET"])
def display_questions():
    modal_id = request.args.get("modal")
    target_body_id = request.args.get("target_body")

    questions = Question.query

    if modal_id:
        questions = questions.filter(Question.modality_id == modal_id)

    if target_body_id:
        questions = questions.filter(Question.target_body_id == target_body_id)

    questions = questions.all()

    modals = Modal.query.all()
    target_bodies = Target.query.all()

    return render_template(
        "question.html",
        questions=questions,
        modals=modals,
        target_bodies=target_bodies,
        current_modal=modal_id,
        current_target_body=target_body_id,
    )


@app.route("/question/<int:question_id>")
def display_question(question_id):
    # Загрузите данные из базы данных для конкретного вопроса
    question = Question.query.get(question_id)
    # Загрузите ответы из базы данных для этого вопроса
    answers = Answer.query.filter_by(id_question=question_id).all()
    return render_template("question_detail.html", question=question, answers=answers)

@app.route("/delete_question/<int:question_id>", methods=["POST"])
def delete_question(question_id):
    question = Question.query.get(question_id)
    if question:
        # Удалить связанные ответы
        answers = Answer.query.filter_by(id_question=question_id).all()
        for answer in answers:
            db.session.delete(answer)

        # Удалить вопрос
        db.session.delete(question)
        db.session.commit()

    return redirect(url_for("display_questions"))

@app.route("/create_question", methods=["GET", "POST"])
def create_question():
    if request.method == "POST":
        # Получаем данные из формы
        text = request.form.get("text")
        image_url = "sdd"  # request.form.get("image_url")
        difficulty_id = request.form.get("difficulty_id")
        modality_id = request.form.get("modality_id")
        target_body_id = request.form.get("target_body_id")

        difficulty = Difficult.query.get(difficulty_id)
        modality = Modal.query.get(modality_id)
        target_body = Target.query.get(target_body_id)

        # Создаем новый объект Question
        question = Question(text=text, image_url=image_url, difficulty=difficulty, modality=modality,
                            target_body=target_body)

        # Добавляем вопрос в сессию
        db.session.add(question)
        db.session.commit()

        # Получаем тексты ответов и их правильность из формы
        answer_texts = request.form.getlist("answer_text[]")
        correct_answers = request.form.getlist("correct_answer[]")
        print(correct_answers)
        question_answ = Question.query.get(question.id)

        # Создаем ответы и сохраняем их в базе данных
        for text, is_correct in zip(answer_texts, correct_answers):
            is_correct_bool = is_correct.lower() == 'true'
            print(text, is_correct, is_correct_bool)
            answer = Answer(name=text, is_correct=is_correct_bool, question_answ=question_answ)
            db.session.add(answer)

        db.session.commit()

        # test = Test(name='Тест 1', description='Описание теста', duration=60)

        # test.questions.append(question)

        # db.session.add(test)
        # db.session.commit()

        return redirect(url_for("create_question"))

    else:
        # Загрузка данных для заполнения выпадающих списков из БД
        difficulties = Difficult.query.all()
        modals = Modal.query.all()
        targets = Target.query.all()
        return render_template("create_question.html", difficulties=difficulties, modals=modals, targets=targets)


# Страница с созданием вопросов
@app.route("/create_tests")
def create_tests():
    return render_template("create_tests.html")


# Страница со статистикой
@app.route("/statistics")
def statistics():
    return render_template("statistics.html")


if __name__ == "__main__":
    app.run(debug=True)

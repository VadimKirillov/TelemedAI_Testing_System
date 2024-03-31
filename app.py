from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import desc

from models import *
from database import create_tables_if_not_exist
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'


# Форма для логина
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Здесь вы можете добавить логику для проверки введенных данных
        # и аутентификации пользователя
        return redirect(url_for('base'))
    return render_template('login.html', form=form)


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
    question = Question.query.get(question_id)
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

        difficulty_id = request.form.get("difficulty_id")
        modality_id = request.form.get("modality_id")
        target_body_id = request.form.get("target_body_id")

        latest_question = Question.query.order_by(desc(Question.id)).first()

        image_url = str(latest_question.id)
        file = request.files['image']
        if file and '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1].lower()
            if extension in {'jpg', 'jpeg', 'png'}:
                image_url += '.' + extension
                full_image_path = os.path.join("static/photo", image_url).replace('\\', '/')
                file.save(os.path.join("static/photo", image_url))

        print("full_image_path",full_image_path)
        difficulty = Difficult.query.get(difficulty_id)
        modality = Modal.query.get(modality_id)
        target_body = Target.query.get(target_body_id)
        print(image_url)
        # Создаем новый объект Question
        question = Question(text=text, image_url=full_image_path, difficulty=difficulty, modality=modality,
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
        return redirect(url_for("create_question"))

    else:
        # Загрузка данных для заполнения выпадающих списков из БД
        difficulties = Difficult.query.all()
        modals = Modal.query.all()
        targets = Target.query.all()
        return render_template("create_question.html", difficulties=difficulties, modals=modals, targets=targets)


# Страница со статистикой
@app.route("/statistics")
def statistics():
    return render_template("statistics.html")


if __name__ == "__main__":
    app.run(debug=True)

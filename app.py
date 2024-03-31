from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import desc

from models import *
from database import create_tables_if_not_exist
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from access import group_permission_decorator
from forms import *
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
IMG_FOLDER = os.path.join("static", "photo")

app.config["UPLOAD_FOLDER"] = IMG_FOLDER

app.config['ACCESS_CONFIG'] = json.load(open('config/access.json', 'r'))





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
     if request.method == 'GET':
         session.clear()
         form = LoginForm()
     else:
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user == None:
                return redirect(url_for('login'))
            if password == user.password:
                with open('config/access.json') as f:
                    data = json.load(f)

                # Поиск соответствия имени пользователя в JSON
                for group_name, permissions in data.items():
                    print(group_name)
                    print(permissions)
                    if user.role == group_name:
                        print("IF")
                        session['group_name'] = group_name
                        session['username'] = username
                        print(session['group_name'])
                        return redirect(url_for('base'))
                else:
                    print("ELSE")
                    session['group_name'] = 'unauthorized'
                    print(session['group_name'])
                    return redirect(url_for('base'))
                # Здесь вы можете добавить логику для проверки введенных данных
                # и аутентификации пользователя
            else:
                return redirect(url_for('login'))
     return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# Страница с тестами
@app.route("/tests")
@group_permission_decorator
def tests():
    all_tests = Test.query.all()
    return render_template("tests.html", all_tests=all_tests)


# Страница с тестами
@app.route("/tests/<int:test_id>", methods=["GET", "POST"])
def start_test(test_id):
    if request.method == "POST":
        return redirect(url_for('main_go_test'))
    else:
        # Обработка GET запроса
        test = Test.query.get(test_id)
        return render_template("start_test.html", test=test)


@app.route("/tests/<int:test_id>/main_go_test", methods=["GET", "POST"])
def main_go_test(test_id):
    return render_template("main_go_test.html")


@app.route("/question", methods=["GET"])
@group_permission_decorator
def display_questions():
    modal_id = request.args.get("modal")
    target_body_id = request.args.get("target_body")

    questions = Question.query.order_by(Question.text)

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


# @app.route("/question/<int:question_id>")
# def display_question(question_id):
#     question = Question.query.get(question_id)
#     answers = Answer.query.filter_by(id_question=question_id).all()
#
#     # Получение данных modal.name, difficult.name, target.name
#     modal_name = question.modality.name
#     difficult_name = question.difficulty.name
#     target_name = question.target_body.name
#
#     return render_template("question_detail.html", question=question, answers=answers,
#                            modal_name=modal_name, difficult_name=difficult_name, target_name=target_name)


@app.route("/question/<int:question_id>", methods=["GET", "POST"])
def display_question(question_id):
    if request.method == "POST":

        question = Question.query.get(question_id)

        text = request.form.get("text")

        difficulty_id = request.form.get("difficulty_id")
        modality_id = request.form.get("modality_id")
        target_body_id = request.form.get("target_body_id")

        difficulty = Difficult.query.get(difficulty_id)
        modality = Modal.query.get(modality_id)
        target_body = Target.query.get(target_body_id)

        question.text = text
        question.difficulty = difficulty
        question.modality = modality
        question.target_body = target_body

        db.session.commit()
        return redirect(url_for("display_questions"))
    else:
        # Загрузка данных для заполнения выпадающих списков из БД
        question = Question.query.get(question_id)

        difficulties = Difficult.query.all()
        modals = Modal.query.all()
        targets = Target.query.all()

        modal_id = question.modality_id
        default_difficulty_id = question.difficulty_id
        target_id = question.target_body_id
        answers = Answer.query.filter_by(id_question=question_id).all()

        return render_template("question_edit.html", question=question, modal_id=modal_id,
                               default_difficulty_id=default_difficulty_id,
                               target_id=target_id, difficulties=difficulties, modals=modals, targets=targets,
                               answers=answers)


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
        latest_question = latest_question.id if latest_question else 0

        image_url = str(latest_question + 1)

        file = request.files['image']
        if file and '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1].lower()
            if extension in {'jpg', 'jpeg', 'png'}:
                image_url += '.' + extension
                path_in_bd = os.path.join("/photo", image_url).replace('\\', '/')
                print("path   ", path_in_bd)
                file.save(os.path.join("static/photo", image_url))

        difficulty = Difficult.query.get(difficulty_id)
        modality = Modal.query.get(modality_id)
        target_body = Target.query.get(target_body_id)
        print(image_url)
        # Создаем новый объект Question
        question = Question(text=text, image_url=path_in_bd, difficulty=difficulty, modality=modality,
                            target_body=target_body)

        # Добавляем вопрос в сессию
        db.session.add(question)
        db.session.commit()

        latest_question_2 = Question.query.order_by(desc(Question.id)).first()
        if latest_question_2 and image_url.split('.')[0] != str(latest_question_2.id):
            image_url = str(latest_question_2.id) + '.' + extension
            full_image_path = os.path.join("static/photo", image_url).replace('\\', '/')

            path_in_bd = os.path.join("/photo", image_url).replace('\\', '/')
            print("path   ", path_in_bd)

            file.save(full_image_path)
            question.image_url = path_in_bd
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
@group_permission_decorator
def statistics():
    return render_template("statistics.html")


if __name__ == "__main__":
    app.run(debug=True)

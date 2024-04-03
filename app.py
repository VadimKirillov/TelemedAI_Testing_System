from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import desc, select, and_

from models import *
from database import create_tables_if_not_exist
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from access import group_permission_decorator
from forms import *
from datetime import datetime, timedelta
import json
import os
import random

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
                        print( " session['username']",session['username'])
                        user = User.query.filter_by(username=username).first()
                        session['id'] = user.id
                        print(session['id'])
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
    if request.method == "POST":
        user_id = session.get('id')
        start_time = datetime.now()  # текущее время
        # Проверяем, существует ли уже попытка теста для данного пользователя и теста с status равным 'in-progress'
        existing_attempt = TestAttempt.query.filter_by(test_id=test_id, user_id=user_id, status='in-progress').first()
        if existing_attempt:
            # Если уже существует попытка теста, выводим сообщение об ошибке
            # current_question = TestAttemptQuestions.query.filter_by(id_attempt=existing_attempt.id).order_by(
            #     desc(TestAttemptQuestions.num)).first()
            current_question = TestAttemptQuestions.query.filter(
                and_(TestAttemptQuestions.id_attempt == existing_attempt.id,
                     TestAttemptQuestions.num != None)).order_by(desc(TestAttemptQuestions.num)).first()
            new_attempt = existing_attempt
            return redirect(url_for("question_page", random_id=current_question.id, test_id=test_id))
            # return redirect(url_for('tests'))
        else:
            print('阿萨')
            # Создаем новую запись в таблице test_attempt
            new_attempt = TestAttempt(
                test_id=test_id,
                user_id=user_id,
                start_time=start_time
            )
            # Добавляем запись в базу данных
            db.session.add(new_attempt)
            db.session.commit()

            test_questions = TestQuestions.query.filter_by(test_id=test_id).all()
            # Создаем записи в таблице TestAttemptQuestions для каждого вопроса
            for test_question in test_questions:
                new_attempt_question = TestAttemptQuestions(
                    id_attempt=new_attempt.id,
                    test=test_question.test_id,
                    question=test_question.question_id,
                    start_time=None,
                    end_time=None,  # Пока не ответили на вопрос, поэтому None
                    num=None,  # Пока не ответили на вопрос, поэтому None
                    correct=None  # Пока не ответили на вопрос, поэтому None
                )
                db.session.add(new_attempt_question)
            db.session.commit()

            # Создаем список для хранения кортежей (id_attempt, test_id)
            filtered_attempt_questions = TestAttemptQuestions.query.filter_by(id_attempt=new_attempt.id,
                                                                              test=test_question.test_id).all()
            id_list = [attempt_question.id for attempt_question in filtered_attempt_questions]

            # print("id_list", id_list)
            random_id = random.choice(id_list)
            attempt_question = TestAttemptQuestions.query.get(random_id)
            attempt_question.num = 1
            db.session.add(attempt_question)
            db.session.commit()
    return redirect(url_for("question_page", random_id=random_id, test_id=test_id))


@app.route("/tests/<int:test_id>/main_go_test/<int:random_id>", methods=["GET", "POST"])
def question_page(random_id, test_id):
    if request.method == "GET":
        start_time = datetime.now()
        # Создаем запись в таблице TestAttemptQuestions
        attempt_question = TestAttemptQuestions.query.get(random_id)
        question = Question.query.get(attempt_question.question)
        answers = Answer.query.filter_by(id_question=question.id).all()
        random.shuffle(answers)
        is_correct_values = []
        # Проходимся по каждому объекту Answer и добавляем его is_correct в массив
        for answer in answers:
            is_correct_values.append(answer.is_correct)
        true_count = is_correct_values.count(True)
        multiple = True if true_count > 1 else False

        if (attempt_question.start_time == None):
            attempt_question.start_time = start_time
            db.session.add(attempt_question)
            db.session.commit()

        time_end = Test.query.get(test_id)
        time_end = time_end.duration
        test_attempt = TestAttempt.query.get(attempt_question.id_attempt)
        begin_time = test_attempt.start_time

        print("begin_time", begin_time)

        new_time = begin_time + timedelta(minutes=time_end)
        time = new_time - start_time
        print("time", time)
        minutes = time.seconds // 60
        seconds = time.seconds % 60
        print("minutes", minutes)
        print("seconds", seconds)
        return render_template("process_test.html", random_id=random_id, test_id=test_id, question=question,
                               answers=answers,
                               multiple=multiple, minutes=minutes, seconds=seconds)
    else:
        selected_answers = request.form.getlist('answers[]')
        attempt_question = TestAttemptQuestions.query.get(random_id)
        question = Question.query.get(attempt_question.question)
        answers = Answer.query.filter_by(id_question=question.id).all()
        correct_answers = []
        for answer in answers:
            if (answer.is_correct):
                correct_answers.append(answer.id)
        selected_answers = [int(ans) for ans in selected_answers]
        selected_answers.sort()
        print("correct_answers", correct_answers)
        print("selected_answers", selected_answers)

        if selected_answers == correct_answers:
            attempt_question.correct = 1
        else:
            attempt_question.correct = 0
        db.session.add(attempt_question)
        db.session.commit()

        end_time = datetime.now()
        attempt_question = TestAttemptQuestions.query.get(random_id)
        if (attempt_question.end_time == None):
            attempt_question.end_time = end_time
        filtered_attempt_questions = TestAttemptQuestions.query.filter_by(id_attempt=attempt_question.id_attempt,
                                                                          test=attempt_question.test, num=None).all()
        if (filtered_attempt_questions):
            id_list = [attempt_question.id for attempt_question in filtered_attempt_questions]
            new_random_id = random.choice(id_list)
            new_attempt_question = TestAttemptQuestions.query.get(new_random_id)
            new_attempt_question.num = attempt_question.num + 1
            db.session.add(new_attempt_question)
            db.session.commit()
        else:
            end_time = datetime.now()
            attempt_question = TestAttemptQuestions.query.get(random_id)
            id_attempt = attempt_question.id_attempt
            test_attempt = TestAttempt.query.get(id_attempt)
            db.session.add(attempt_question)
            db.session.commit()

            test_attempt.status = 'done'
            test_attempt.end_time = end_time
            db.session.add(test_attempt)
            db.session.commit()
            return redirect(url_for("end_test", id_attempt=id_attempt))
        return redirect(url_for("question_page", random_id=new_random_id, test_id=test_id))


@app.route("/tests/<int:id_attempt>/end_test")
def end_test(id_attempt):
    return render_template("end_test.html")


@app.route("/question", methods=["GET"])
@group_permission_decorator
def display_questions():
    modal_id = request.args.get("modal")
    target_body_id = request.args.get("target_body")
    search_text = request.args.get('search_text', '')

    questions = Question.query.order_by(Question.text)

    if modal_id:
        questions = questions.filter(Question.modality_id == modal_id)

    if target_body_id:
        questions = questions.filter(Question.target_body_id == target_body_id)

    # Фильтруем вопросы по тексту
    if search_text:
        questions = questions.filter(Question.text.ilike(f"%{search_text}%"))

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
        current_search_text=search_text
    )


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
        print("question_id ", question_id)
        return render_template("question_edit.html", question_id=question_id, question=question, modal_id=modal_id,
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
        test_questions = TestQuestions.query.filter_by(question_id=question_id).all()
        for test_question in test_questions:
            db.session.delete(test_question)
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
                tmp_flag = 0
        else:
            # Если файл не был загружен, используем путь по умолчанию
            image_url = "/photo/default.jpg"
            tmp_flag = 1
            path_in_bd = image_url
            print("path_in_bd", path_in_bd)

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
        if latest_question_2 and image_url.split('.')[0] != str(latest_question_2.id) and tmp_flag ==0:
            image_url = str(latest_question_2.id) + '.' + extension
            full_image_path = os.path.join("static/photo", image_url).replace('\\', '/')

            path_in_bd = os.path.join("/photo", image_url).replace('\\', '/')
            print("path   ", path_in_bd)

            file.save(full_image_path)
            question.image_url = path_in_bd
            db.session.commit()
        else:
            path_in_bd = "/photo/default.jpg"
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
    # Получить количество вопросов по категориям сложности
    difficulty_counts = db.session.query(Difficult.name, db.func.count(Question.difficulty_id)).join(Question).group_by(
        Difficult.name).all()

    # Получить количество вопросов по модальностям
    modality_counts = db.session.query(Modal.name, db.func.count(Question.modality_id)).join(Question).group_by(
        Modal.name).all()

    # Получить количество вопросов по целевым областям тела
    target_counts = db.session.query(Target.name, db.func.count(Question.target_body_id)).join(Question).group_by(
        Target.name).all()

    return render_template("statistics.html", difficulty_counts=difficulty_counts, modality_counts=modality_counts,
                           target_counts=target_counts)


if __name__ == "__main__":
    app.run(debug=True)

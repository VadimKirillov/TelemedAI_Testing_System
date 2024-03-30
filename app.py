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


# Страница с вопросами
@app.route("/question")
def question():
    return render_template("question.html")


# Маршрут для страницы создания вопросов и сохранения данных
@app.route("/create_question", methods=["GET", "POST"])
def create_question():
    if request.method == "POST":
        # Получаем данные из формы
        text = request.form.get("text")
        image_url = request.form.get("image_url")
        difficulty_id = request.form.get("difficulty_id")
        modality_id = request.form.get("modality_id")
        target_body_id = request.form.get("target_body_id")
        print(text, image_url, difficulty_id, modality_id, target_body_id)
        # Создаем новый объект Question
        question = Question(text=text, image_url=image_url, difficulty=difficulty_id, modality=modality_id,
                            target_body=target_body_id)

        # Добавляем вопрос в сессию
        db.session.add(question)
        # Сохраняем изменения в базе данных
        db.session.commit()

        # После сохранения вопроса происходит перенаправление на эту же страницу
        return redirect(url_for("question"))

    # Если метод запроса GET, просто отображаем страницу создания вопросов
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

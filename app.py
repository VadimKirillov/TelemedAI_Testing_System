from flask import Flask, render_template, request
from models import db
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

from flask import Flask, render_template, request

app = Flask(__name__)


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

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    options = db.relationship('Option', backref='question', lazy='dynamic')
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    questions = db.relationship('Question', backref='test', lazy='dynamic')


class UserAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    test = db.relationship('Test', backref='attempts')

def create_tables_if_not_exist():
    engine = db.engine()
    if not engine.dialect.has_table(engine, 'question') or \
            not engine.dialect.has_table(engine, 'option') or \
            not engine.dialect.has_table(engine, 'test') or \
            not engine.dialect.has_table(engine, 'user_attempt'):
        db.create_all()
        print("Таблицы созданы.")
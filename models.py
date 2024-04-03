from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import BYTEA

db = SQLAlchemy()


class TestQuestions(db.Model):
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)

    test = db.relationship("Test", backref=db.backref('testQuestions', lazy='dynamic'))

    question = db.relationship("Question", backref=db.backref('testQuestions', lazy='dynamic'))


# Таблица с вопросами
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('difficult.id'), nullable=False)
    modality_id = db.Column(db.Integer, db.ForeignKey('modal.id'), nullable=False)
    target_body_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)

    difficulty = db.relationship('Difficult', backref=db.backref('questions', lazy='dynamic'))
    modality = db.relationship('Modal', backref=db.backref('questions', lazy='dynamic'))
    target_body = db.relationship('Target', backref=db.backref('questions', lazy='dynamic'))


class Difficult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    rank = db.Column(db.Integer, nullable=False)


class Modal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    id_question = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question_answ = db.relationship('Question', backref=db.backref('answers', lazy='dynamic'))


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.Integer, nullable=False)

    # questions = db.relationship('Question', secondary=TestQuestions, backref='tests')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), default='user')


class TestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='in-progress')  # Possible values: 'in-progress', 'completed'

    test = db.relationship('Test', backref='attempts')
    user = db.relationship('User', backref='attempts')


class TestAttemptQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_attempt = db.Column(db.Integer, db.ForeignKey('test_attempt.id'), nullable=False)
    test = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Integer, nullable=False)

    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)

    num = db.Column(db.Integer, nullable=True)
    correct = db.Column(db.Integer, nullable=True)  # 0 or 1

    attempt_questions = db.relationship('TestAttempt', backref=db.backref('test_attempt_questions', lazy='dynamic'))


def create_tables_if_not_exist():
    engine = db.engine()
    if not engine.dialect.has_table(engine, 'question') or \
            not engine.dialect.has_table(engine, 'difficult') or \
            not engine.dialect.has_table(engine, 'modal') or \
            not engine.dialect.has_table(engine, 'target') or \
            not engine.dialect.has_table(engine, 'answer'):
        db.create_all()
        print("Таблицы созданы.")

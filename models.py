from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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




def create_tables_if_not_exist():
    engine = db.engine()
    if not engine.dialect.has_table(engine, 'question') or \
            not engine.dialect.has_table(engine, 'difficult') or \
            not engine.dialect.has_table(engine, 'modal') or \
            not engine.dialect.has_table(engine, 'target') or \
            not engine.dialect.has_table(engine, 'answer'):
        db.create_all()
        print("Таблицы созданы.")

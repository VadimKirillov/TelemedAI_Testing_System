from models import db
from sqlalchemy import inspect

# TODO проверить все таблицы
def create_tables_if_not_exist():
    connection = db.engine.connect()
    inspector = inspect(connection)
    if not inspector.has_table('question') or \
            not inspector.has_table('option') or \
            not inspector.has_table('test') or \
            not inspector.has_table('user_attempt'):
        db.create_all()
        print("Таблицы созданы.")

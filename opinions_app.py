from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# Подключить БД SQLite.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# Создать экземпляр SQLAlchemy и в качестве параметра
# передать в него экземпляр приложения Flask.
db = SQLAlchemy(app)

@app.route('/')
def index_view():
    # print(app.config)
    return 'Совсем скоро тут будет случайное мнение о фильме!'

if __name__ == '__main__':
    app.run()
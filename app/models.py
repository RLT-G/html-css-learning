from app import app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
db.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    name = db.Column(db.String(100), unique=True, primary_key=True)
    gender = db.Column(db.String(100), unique=True, primary_key=True)
    password = db.Column(db.String(100), unique=True, primary_key=True)
    data = db.Column(db.String(100), unique=True, primary_key=True)
    number_phone = db.Column(db.String(100), unique=True, primary_key=True)
    about = db.Column(db.String(100), unique=True, primary_key=True)
    country = db.Column(db.String(100), unique=True, primary_key=True)
    image = db.Column(db.LargeBinary, unique=True, primary_key=True)

    def __init__(self, name, gender, data, password, number_phone, about, country, image):
        self.name = name
        self.gender = gender
        self.data = data
        self.password = password
        self.number_phone = number_phone
        self.about = about
        self.country = country
        self.image = image


class Forum(UserMixin, db.Model):
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    title = db.Column(db.String(100), primary_key=True)
    full_text = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), primary_key=True)
    date = db.Column(db.String(100), primary_key=True)

    def __init__(self, title, full_text, name, date):
        self.title = title
        self.full_text = full_text
        self.name = name
        self.date = date


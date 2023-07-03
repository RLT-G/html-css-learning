from flask import Flask
from flask_session import Session
import os


app = Flask(__name__)
# app.config.from_object('config.DevelopementConfig')
app.config.from_object('config.ProductionConfig')
Session(app)


from . import views
from flask import Flask
from model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_share.db'

db.init_app(app)
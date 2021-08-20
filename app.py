from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:6456/postgres"
app.config["SQLALCHEMY_BINDS"] = {
    "second": "postgresql://postgres:postgres@localhost:7845/postgres"
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    name = db.Column(db.String(128), primary_key=True)
    date = db.Column(db.DateTime())
    department = db.Column(db.String(128))


class User_Second(db.Model):
    __bind_key__ = "second"
    name = db.Column(db.String(128), primary_key=True)
    date = db.Column(db.DateTime())
    department = db.Column(db.String(128))

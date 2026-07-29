from extensions import db
from datetime import datetime

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    biz = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    service = db.Column(db.String(100))
    status = db.Column(db.String(50))
    date = db.Column(db.String(20))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String(100))
    type = db.Column(db.String(100))
    start = db.Column(db.String(20))
    end = db.Column(db.String(20))
    status = db.Column(db.String(50))
    progress = db.Column(db.Integer, default=0)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    msg = db.Column(db.Text)
    status = db.Column(db.String(50), default='Nuevo')

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    desc = db.Column(db.String(255))
    url = db.Column(db.String(255))
    link = db.Column(db.String(255))

class PublicReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initials = db.Column(db.String(10))
    stars = db.Column(db.Integer, default=5)
    name = db.Column(db.String(100))
    biz = db.Column(db.String(100))
    text = db.Column(db.Text)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(60))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

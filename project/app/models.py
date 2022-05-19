from enum import unique
from app import db

class Attack(db.Model):
    attackId = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    fileName = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    usage = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Report(db.Model):
    reportId = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, nullable=False)
    attackId = db.Column(db.Integer, nullable=False)
    startTime = db.Column(db.String(100), nullable=False)
    log = db.Column(db.Text(), nullable=False)
    result = db.Column(db.Text(), nullable=True)
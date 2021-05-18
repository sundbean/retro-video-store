from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db

class Video(db.Model):
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    release_date = db.Column(db.Datetime)
    total_inventory = db.Column(db.Integer)
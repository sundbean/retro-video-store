from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db


# https://stackoverflow.com/questions/36579355/sqlalchemy-set-default-value-of-one-column-to-that-of-another-column
def default_available_inventory(context):
    return context.get_current_parameters()['total_inventory']

class Video(db.Model):
    video_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime)
    genre = db.Column(ARRAY(String))
    total_inventory = db.Column(db.Integer)
    available_inventory = db.Column(db.Integer, default=default_available_inventory)

    def get_video_info(self):
        video_info = {
            "id": self.video_id,
            "title": self.title,
            "release_date": self.release_date,
            "genre": self.genre,
            "total_inventory": self.total_inventory,
            "available_inventory": self.available_inventory
        }
        return video_info

    def from_json(self, request_body):
        self.title = request_body['title']
        self.release_date = request_body['release_date']
        self.total_inventory = request_body['total_inventory']
        self.genre = request_body['genre']
        return self
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db

class Video(db.Model):
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime)
    total_inventory = db.Column(db.Integer)

    def get_video_info(self):
        video_info = {
            "id": self.video_id,
            "title": self.title,
            "release_date": self.release_date,
            "total_inventory": self.total_inventory,
            "available_inventory": self.total_inventory
        }
        return video_info

    def from_json(self, request_body):
        self.title = request_body['title']
        self.release_date = request_body['release_date']
        self.total_inventory = request_body['total_inventory']
        return self
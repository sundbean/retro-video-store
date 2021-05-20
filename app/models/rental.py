from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.customer import Customer
from app.models.video import Video

class Rental(db.Model):
    due_date = db.Column(db.DateTime)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.video_id'), primary_key=True)

    def get_rental_info(self):
        rental_info = {
            "customer_id": self.customer_id,
            "video_id": self.video_id,
            "due_date": self.due_date,
            "videos_checked_out_count": Customer.query.get(self.customer_id).videos_checked_out_count,
            "available_inventory": Video.query.get(self.video_id).available_inventory
        }
        return rental_info
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.customer import Customer
from app.models.video import Video

class Rental(db.Model):
    rental_id = db.Column(db.Integer, primary_key=True)
    due_date = db.Column(db.DateTime)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.video_id'), primary_key=True)

    def get_videos_for_customer(self, id_of_customer):
        results = db.session.query(Customer, Video, Rental)\
            .join(Customer, Customer.customer_id==Rental.customer_id)\
            .join(Video, Video.video_id==Rental.video_id)\
            .filter(Customer.customer_id==id_of_customer).all()
        return results

    def get_customers_for_video(self, id_of_video):
        results = db.session.query(Customer, Video, Rental)\
            .join(Video, Video.video_id==Rental.video_id)\
            .join(Customer, Customer.customer_id==Rental.customer_id)\
            .filter(Video.video_id==id_of_video).all()
        return results
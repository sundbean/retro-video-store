from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    postal_code = db.Column(db.String)
    phone = db.Column(db.String)
    registered_at = db.Column(db.Datetime)

    def get_customer_info(self):
        customer_info = {
            "id": self.customer_id,
            "name": self.name,
            "registered_at": self.registered_at,
            "postal_code": self.postal_code,
            "phone": self.phone
            "videos_checked_out_count": 0
        }
        return customer_info

    def from_json(self, request_body):
        self.name = request_body['name']
        self.postal_code = request_body['postal_code']
        self.phone = request_body['phone']
        return self
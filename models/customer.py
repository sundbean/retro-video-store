from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    postal_code = db.Column(db.Integer)
    phone = db.Column(db.String)
    register_at = db.Colum(db.Datetime)
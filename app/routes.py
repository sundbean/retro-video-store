from flask import Blueprint, make_response, request, jsonify
from app import db
from app.models.video import Video
from app.models.customer import Customer
import requests
import os

videos_bp = Blueprint("videos", __name__, url_prefix="/videos")
customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

#######################################################
################ CRUD CUSTOMERS #######################
#######################################################

# Exceptions for requests
# https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module

# try:
#     ...
# except requests.exceptions.RequestException as e:
#     ...

@customers_bp.route("", methods=["GET"])
def get_all_customers():
    customers = Customer.query.all()

    return jsonify([customer.get_customer_info() for customer in customers])


@customers_bp.route("", methods=["POST"])
def post_new_customer():
    request_body = request.get_json()

    try:
        new_customer = Customer(name=request_body["name"],
                                postal_code=request_body["postal_code"],
                                phone=request_body["phone"])
    except KeyError as e:
        return make_response(detail_error("Invalid data"), 400)

    db.session.add(new_customer)
    db.session.commit()

    response = {
        "id": new_customer.customer_id
    }

    return make_response(jsonify(response), 201)


@customers_bp.route("/<customer_id>", methods=["GET"])
def get_single_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    return jsonify(customer.get_customer_info())


@customers_bp.route("/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    request_body = request.get_json()

    try:
        customer = customer.from_json(request_body)
    except KeyError as e:
        return make_response(detail_error("Invalid or missing data"), 400)

    db.session.commit()

    return customer.get_customer_info()


@customers_bp.route("/<customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    db.session.delete(customer)
    db.session.commit()

    return {
        "id": customer.customer_id
    }



##########################################################
###################### CRUD VIDEOS #######################
##########################################################

@videos_bp.route("", methods=["GET"])
def get_all_videos():
    pass

@videos_bp.route("", methods=["POST"])
def post_new_customer():
    pass

@videos_bp.route("/<video_id>", methods=["GET"])
def get_single_video(video_id):
    pass

@videos_bp.route("/<video_id>", methods=["PUT"])
def update_video(video_id):
    pass

@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    pass



##################### HELPER FUNCTIONS #####################

def detail_error(error):
    return {
        "errors": [
            error
        ]
    }
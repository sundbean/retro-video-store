from flask import Blueprint, make_response, request, jsonify
from app import db
from app.models.video import Video
from app.models.customer import Customer
from app.models.rental import Rental
from sqlalchemy import exc
import datetime
import requests
import os

videos_bp = Blueprint("videos", __name__, url_prefix="/videos")
customers_bp = Blueprint("customers", __name__, url_prefix="/customers")
rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")

#######################################################
################### CRUD CUSTOMERS ####################
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
    except (KeyError, TypeError, exc.SQLAlchemyError) as e:
        return make_response(detail_error("Invalid data"), 400)

    db.session.add(new_customer)
    db.session.commit()

    return make_response({
        "id": new_customer.customer_id
    }, 201)


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
    except (KeyError, TypeError, exc.SQLAlchemyError) as e:
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
    videos = Video.query.all()

    return jsonify([video.get_video_info() for video in videos])


@videos_bp.route("", methods=["POST"])
def post_new_customer():
    request_body = request.get_json()

    try:
        new_video = Video(title=request_body["title"],
                            release_date=request_body['release_date'],
                            total_inventory=request_body['total_inventory'])
    except (KeyError, TypeError, exc.SQLAlchemyError):
        return make_response(detail_error("Missing or invalid data"), 400)

    db.session.add(new_video)
    db.session.commit()

    return make_response({
        "id": new_video.video_id
    }, 201)


@videos_bp.route("/<video_id>", methods=["GET"])
def get_single_video(video_id):
    video = Video.query.get(video_id)
    if video is None:
        return make_response(detail_error("Video does not exist"), 404)
    
    return jsonify(video.get_video_info())


@videos_bp.route("/<video_id>", methods=["PUT"])
def update_video(video_id):
    video = Video.query.get(video_id)
    if video is None:
        return make_response(detail_error("Video does not exist"), 404)

    request_body = request.get_json()

    try:
        video = video.from_json(request_body)
    except KeyError as e:
        return make_response(detail_error("Invalid or missing data"), 400)

    db.session.commit()

    return jsonify(video.get_video_info())


@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if video is None:
        return make_response(detail_error("Video does not exist"), 404)

    db.session.delete(video)
    db.session.commit()

    return {
        "id": video.video_id
    }


#######################################################
################### CRUD RENTALS ######################
#######################################################

@rentals_bp.route("/check-out", methods=["POST"])
def check_out_video_to_customer():
    request_body = request.get_json()

    try:
        video = Video.query.get(request_body["video_id"])
    except exc.SQLAlchemyError as err:
        return make_response(detail_error("Video does not exist"), 404)
    if video.available_inventory == 0:
        return make_response(detail_error("No available inventory for that title"), 400)

    try:
        customer = Customer.query.get(request_body["customer_id"])
    except exc.SQLAlchemyError as err:
        return make_response(detail_error("Customer does not exist"), 404)

    rental = Rental(customer_id=request_body["customer_id"],
                            video_id=request_body["video_id"],
                            due_date=datetime.datetime.now() + datetime.timedelta(days=7))

    video.available_inventory = video.available_inventory - 1
    customer.videos_checked_out_count = customer.videos_checked_out_count + 1

    db.session.commit()

    return make_response(rental.get_rental_info())


##################### HELPER FUNCTIONS #####################

def detail_error(error):
    return {
        "errors": [
            error
        ]
    }
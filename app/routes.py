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

@customers_bp.route("", methods=["GET"])
def get_all_customers():
    """
    Input: none
    Output: 200 OK, Returns a JSON list of customer dictionaries that detail customer information of all customers in database.
    (Returned list is of all customers, sorted by ascending customer_id, unless query parameters specify otherwise)
    """
    sort_query = request.args.get("sort")
    filter_by_query = request.args.get("filter_by")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "customer_id"

    customers = query_with_parameters(Customer, sort_query, filter_by_query, page_to_return, results_per_page)

    return jsonify([customer.get_customer_info() for customer in customers])


@customers_bp.route("", methods=["POST"])
def post_new_customer():
    """
    Input: Request body = JSON dictionary with keys "name," "postal code," "phone."
    Action: Using input information, adds new customer row to customer table in database.
    Output: 201 Created with JSON dictionary containing id of newly added customer.
    """
    request_body = request.get_json()

    try:
        new_customer = Customer(name=request_body["name"],
                                postal_code=request_body["postal_code"],
                                phone=request_body["phone"],
                                registered_at=datetime.datetime.now())
    except (KeyError, TypeError, exc.SQLAlchemyError) as e:
        return make_response(detail_error("Invalid data"), 400)

    db.session.add(new_customer)
    db.session.commit()

    return make_response({
        "id": new_customer.customer_id
    }, 201)


@customers_bp.route("/<customer_id>", methods=["GET"])
def get_single_customer(customer_id):
    """
    Input: Customer id (in route)
    Output: 200 OK, JSONified dictionary of customer information for specified customer id.
    """
    
    customer = Customer.query.get(customer_id)
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    return jsonify(customer.get_customer_info())


@customers_bp.route("/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """
    Input: Customer id (in route), Request body = JSON dictionary with keys "name," "phone," "postal_code".
    Action: Updates customer information in database's customer table at specified customer id.
    Output: 200 OK, JSON (automatically converted) dictionary with updated customer information.
    """
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
    """
    Input: Customer id (in route)
    Action: Deletes customer row in database's customer table at specified customer id.
    Output: 200 OK, JSON (automatically converted) dictionary with id of deleted customer.
    """
    customer = Customer.query.get(customer_id)
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    db.session.delete(customer)
    db.session.commit()

    return {
        "id": customer.customer_id
    }

# BUG IN OPTIONAL ENHANCEMENT: When a video has been checked out more than once by the same customer, 
# the rental only shows up once in the response. Why? This also ONLY applies if I'm trying to get both
# rental records in the same response. If I include query parameters for p and n that separates the 
# similar records into different pages, I can get each record by submitting multiple requests with different
# p params.
@customers_bp.route("/<customer_id>/rentals", methods=["GET"])
def get_rentals_by_customer(customer_id):
    """
    Input: Customer id (in route)
    Output: 200 OK, JSON list of rental information dictionaries
    """
    if Customer.query.get(customer_id) is None:
        return make_response(detail_error("Customer does not exist"), 404)

    # This query gets all rental objects for specified customer id
    rentals = db.session.query(Rental)\
        .join(Customer, Customer.customer_id==Rental.customer_id)\
        .join(Video, Video.video_id==Rental.video_id)\
        .filter(Customer.customer_id==customer_id)

    # Lets consider query parameters in our resulting list of rentals
    sort_query = request.args.get("sort")
    filter_by_query = request.args.get("filter_by")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "customer_id"

    # Narrow down our results list according to query parameters
    rentals = rentals_with_parameters(rentals, sort_query, filter_by_query, page_to_return, results_per_page)

    results = []
    for rental in rentals:
        video = Video.query.get(rental.video_id)
        results.append({
            "release_date": video.release_date,
            "title": video.title,
            "due_date": rental.due_date
        })
    
    return jsonify(results)

    


##########################################################
###################### CRUD VIDEOS #######################
##########################################################

@videos_bp.route("", methods=["GET"])
def get_all_videos():
    """
    Input: none
    Output: 200 OK, JSON list of dictionaries containing information for each video in video table
    (Default response is list of ALL videos ordered by video_id, unless query parameters specify otherwise)
    """
    sort_query = request.args.get("sort")
    filter_by_query = request.args.get("filter_by")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "video_id"

    videos = query_with_parameters(Video, sort_query, filter_by_query, page_to_return, results_per_page)

    return jsonify([video.get_video_info() for video in videos])


@videos_bp.route("", methods=["POST"])
def post_new_customer():
    """
    Input: Request body = JSON dictionary with keys "title," "release_date," "total_inventory"
    Action: Adds new row to video table with video information provided in the request body
    Output: 201 Created response with JSON dictionary containing newly added video's id
    """
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
    """
    Input: video id (in route)
    Output: 200 OK, JSON dictionary of video information for specified video id
    """
    video = Video.query.get(video_id)
    if video is None:
        return make_response(detail_error("Video does not exist"), 404)
    
    return jsonify(video.get_video_info())


@videos_bp.route("/<video_id>", methods=["PUT"])
def update_video(video_id):
    """
    Input: Video id (in route), JSON dictionary with keys "title", "release_date", "total_inventory" (required)
    Action: Updates video information in database's video table at specified video id.
    Output: 200 OK, JSON dictionary containing details of updated video.
    """
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
    """
    Input: Video id (in route)
    Action: Deletes row in video table at specified video id
    Output: 200 OK, JSON dictionary containing id of deleted video
    """
    video = Video.query.get(video_id)
    if video is None:
        return make_response(detail_error("Video does not exist"), 404)

    db.session.delete(video)
    db.session.commit()

    return {
        "id": video.video_id
    }


# BUG IN OPTIONAL ENHANCEMENT: When a video has been checked out more than once by the same customer, 
# the rental only shows up once in the response. Why? This also ONLY applies if I'm trying to get both
# rental records in the same response. If I include query parameters for p and n that separates the 
# similar records into different pages, I can get each record by submitting multiple requests with different
# p params.
@videos_bp.route("/<video_id>/rentals", methods=["GET"])
def get_rentals_by_video(video_id):
    """
    Input: video id (in route)
    Output: 200 OK, JSON list of dictionaries containing details of each rental for the specified video id
    """
    if Video.query.get(video_id) is None:
        return make_response(detail_error("Video does not exist"), 404)

    # This query gets all rental objects at specified video id
    rentals = db.session.query(Rental)\
        .join(Video, Video.video_id==Rental.video_id)\
        .join(Customer, Customer.customer_id==Rental.customer_id)\
        .filter(Video.video_id==video_id)

    # Lets consider query parameters in our resulting list of rentals
    sort_query = request.args.get("sort")
    filter_by_query = request.args.get("filter_by")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "video_id"

    # Narrow down our results list according to query parameters
    rentals = rentals_with_parameters(rentals, sort_query, filter_by_query, page_to_return, results_per_page)

    results = []
    for rental in rentals:
        customer = Customer.query.get(rental.customer_id)
        results.append({
            "due_date": rental.due_date,
            "name": customer.name,
            "phone": customer.phone,
            "postal_code": customer.postal_code
        })
    
    return jsonify(results)




#######################################################
################### CRUD RENTALS ######################
#######################################################

@rentals_bp.route("/check-out", methods=["POST"])
def check_out_video_to_customer():
    """
    Input: Request body = JSON dictionary with required keys "customer_id", "video_id"
    Action: Adds new row in rental table using details provided in request body. Updates video and customer
    information accordingly to "check out" the video to the customer. 
    Output: 200 OK, JSON dictionary containing details of newly added rental.
    """
    request_body = request.get_json()

    try:
        video = Video.query.get(request_body["video_id"])
        if video is None:
            make_response(detail_error("Video does not exist"), 404)
    except exc.SQLAlchemyError as err:
        return make_response(detail_error("Invalid video id"), 400)

    if video.available_inventory == 0:
        return make_response(detail_error("No available inventory for that title"), 400)

    try:
        customer = Customer.query.get(request_body["customer_id"])
        if customer is None:
            return make_response(detail_error("Customer does not exist"), 404)
    except exc.SQLAlchemyError as err:
        return make_response(detail_error("Invalid customer id"), 400)

    new_rental = Rental(customer_id=request_body["customer_id"],
                            video_id=request_body["video_id"],
                            due_date=datetime.datetime.now() + datetime.timedelta(days=7))

    video.available_inventory = video.available_inventory - 1
    customer.videos_checked_out_count = customer.videos_checked_out_count + 1

    db.session.add(new_rental)
    db.session.commit()

    return make_response(new_rental.get_rental_info())


@rentals_bp.route("/check-in", methods=["POST"])
def check_in_rented_video():
    """
    Input: Request body = JSON dictionary with required keys "video_id" and "customer_id"
    Action: "Checks in" the rental by updating customer and video information to reflect the return of the video, 
    and deletes rental record from rental table.
    Output: 200 OK, JSON dictionary with details of newly deleted rental.
    """
    request_body = request.get_json()

    customer = Customer.query.get(request_body["customer_id"])
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    video = Video.query.get(request_body["video_id"])
    if video is None:
        return make_response(detail_error("Video does not exist"), 404)

    rental = Rental.query.get({"video_id": request_body["video_id"], "customer_id": request_body["customer_id"]})
    if rental is None:
        return make_response(detail_error("No matching record"), 400)

    video.available_inventory = video.available_inventory + 1
    customer.videos_checked_out_count = customer.videos_checked_out_count - 1

    response = rental.get_rental_info()
    del response["due_date"]

    db.session.delete(rental)
    db.session.commit()

    return response



##################### HELPER FUNCTIONS #####################

def detail_error(error):
    """
    Input: Error message (string) detailing error
    Output: Dictionary with error details for JSON response
    """
    return {
        "errors": [
            error
        ]
    }

def query_with_parameters(model_name, order_by=None, filter_by=None, page=0, results_per_page=None):
    query = db.session.query(model_name)
    if order_by:
        query = query.order_by(order_by)
    if filter_by:
        query = query.filter_by(filter_by)
    if results_per_page:
        query = query.limit(results_per_page)
    if page:
        page = int(page) - 1
        query = query.offset(page * int(results_per_page))
    return query

def rentals_with_parameters(rentals_list, order_by=None, filter_by=None, page=0, results_per_page=None):
    query = rentals_list
    if order_by:
        query = query.order_by(order_by)
    if filter_by:
        query = query.filter_by(filter_by)
    if results_per_page:
        query = query.limit(results_per_page)
    if page:
        page = int(page) - 1
        query = query.offset(page * int(results_per_page))
    return query
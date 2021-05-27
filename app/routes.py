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
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "customer_id"

    customers = query_with_parameters(Customer, sort_query, page_to_return, results_per_page)

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


@customers_bp.route("/<customer_id>/rentals", methods=["GET"])
def get_rentals_by_customer(customer_id):
    """
    Input: Customer id (in route)
    Output: 200 OK, JSON list of rental information dictionaries
    """
    customer = Customer.query.get(customer_id)
    if customer is None:
        return make_response(detail_error("Customer does not exist"), 404)

    # This query gets all rental objects for specified customer id
    rentals = db.session.query(Rental)\
        .join(Customer, Customer.customer_id==Rental.customer_id)\
        .join(Video, Video.video_id==Rental.video_id)\
        .filter(Customer.customer_id==customer_id)

    # Lets consider query parameters in our resulting list of rentals
    sort_query = request.args.get("sort")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    # Narrow down our results list according to query parameters
    rentals = get_rentals_within_parameters(rentals, sort_query, page_to_return, results_per_page)

    results = []
    for rental in rentals:
        video = Video.query.get(rental.video_id)
        results.append({
            "release_date": video.release_date,
            "title": video.title,
            "due_date": rental.due_date
        })
    
    return jsonify(results)

    
# OPTIONAL ENHANCEMENT
@customers_bp.route("/<customer_id>/history", methods=["GET"])
def get_rental_history_for_customer(customer_id):
    """
    Input: URI parameter customer ID
    Output: JSON list of dictionaries containing details of specified custoner's rental history.
    """
    if Customer.query.get(customer_id) is None:
        return make_response(detail_error("Customer does not exist"), 404)

    # This query gets all rental objects at specified customer id
    rentals = db.session.query(Rental)\
        .join(Video, Video.video_id==Rental.video_id)\
        .join(Customer, Customer.customer_id==Rental.customer_id)\
        .filter(Customer.customer_id==customer_id)\
        .filter(Rental.returned_on_date != None)

    # Lets consider query parameters in our resulting list of rentals
    sort_query = request.args.get("sort")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    # Narrow down our results list according to query parameters
    rentals = get_rentals_within_parameters(rentals, sort_query, page_to_return, results_per_page)

    results = []
    for rental in rentals:
        checkout_date = rental.due_date - datetime.timedelta(days=7)
        video = Video.query.get(rental.video_id)
        results.append({
            "title": video.title,
            "checkout_date": checkout_date,
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
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "video_id"

    videos = query_with_parameters(Video, sort_query, page_to_return, results_per_page)

    return jsonify([video.get_video_info() for video in videos])


@videos_bp.route("", methods=["POST"])
def post_new_video():
    """
    Input: Request body = JSON dictionary with keys "title," "release_date," "total_inventory", "genre"
    Action: Adds new row to video table with video information provided in the request body
    Output: 201 Created response with JSON dictionary containing newly added video's id
    """
    request_body = request.get_json()

    try:
        new_video = Video(title=request_body["title"],
                            release_date=request_body['release_date'],
                            genre=request_body['genre'],
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
        .filter(Video.video_id==video_id)\
        .filter(Rental.returned_on_date==None)

    # Lets consider query parameters in our resulting list of rentals
    sort_query = request.args.get("sort")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    # Narrow down our results list according to query parameters
    rentals = get_rentals_within_parameters(rentals, sort_query, page_to_return, results_per_page)

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


# OPTIONAL ENHANCEMENT
@videos_bp.route("/<video_id>/history", methods=["GET"])
def get_rental_history_for_video(video_id):
    """
    Input: URI parameter "video_id"
    Output: A JSON list of dictionaries that detail customer information for videos that have been checked out in the past.
    """
    if Video.query.get(video_id) is None:
        return make_response(detail_error("Video does not exist"), 404)

    # This query gets all rental objects at specified video id
    rentals = db.session.query(Rental)\
        .join(Video, Video.video_id==Rental.video_id)\
        .join(Customer, Customer.customer_id==Rental.customer_id)\
        .filter(Video.video_id==video_id)\
        .filter(Rental.returned_on_date != None)

    # Lets consider query parameters in our resulting list of rentals
    sort_query = request.args.get("sort")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    # Narrow down our results list according to query parameters
    rentals = get_rentals_within_parameters(rentals, sort_query, page_to_return, results_per_page)

    results = []
    for rental in rentals:
        checkout_date = rental.due_date - datetime.timedelta(days=7)
        customer = Customer.query.get(rental.customer_id)
        results.append({
            "customer_id": customer.customer_id,
            "name": customer.name,
            "postal_code": customer.postal_code,
            "checkout_date": checkout_date,
            "due_date": rental.due_date
        })
    
    return jsonify(results)


#######################################################
################### CRUD RENTALS ######################
#######################################################

# OPTIONAL ENHANCEMENT
@rentals_bp.route("", methods=["GET"])
def get_info_for_all_rentals():
    """
    Input: None
    Output: A JSON list of dictionaries containing details for every rental in rental table.
    """
    sort_query = request.args.get("sort")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    rentals = query_with_parameters(Rental, sort_query, page_to_return, results_per_page)
    
    return jsonify([rental.get_rental_info() for rental in rentals])


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
    if rental.returned_on_date:
        return make_response(detail_error("Rental has already been checked in"), 400)

    video.available_inventory = video.available_inventory + 1
    customer.videos_checked_out_count = customer.videos_checked_out_count - 1

    rental.returned_on_date = datetime.datetime.now()

    response = rental.get_rental_info()
    del response["due_date"]

    db.session.commit()

    return response


# OPTIONAL ENHANCEMENT
@rentals_bp.route("/overdue", methods=["GET"])
def get_overdue_rentals():
    """
    Input: optional query parameters are sort, n for num per page, and p for page
    Output: A JSON list of rentals (and associated information) that are overdue.
    """
    # Get all rentals that are past due
    rentals = Rental.query.filter(Rental.due_date < datetime.datetime.now()).filter(Rental.returned_on_date==None)

    sort_query = request.args.get("sort")
    results_per_page = request.args.get("n")
    page_to_return = request.args.get("p")

    if not sort_query:
        sort_query = "video_id"

    # Narrow down our rentals list by the query parameters
    rentals = get_rentals_within_parameters(rentals, sort_query, page_to_return, results_per_page)

    results = []
    for rental in rentals:
        checkout_date = rental.due_date - datetime.timedelta(days=7)
        customer = Customer.query.get(rental.customer_id)
        video = Video.query.get(rental.video_id)
        results.append({
            "video_id": video.video_id,
            "title": video.title,
            "customer_id": customer.customer_id,
            "name": customer.name,
            "postal_code": customer.postal_code,
            "checkout_date": checkout_date,
            "due_date": rental.due_date
        })

    return jsonify(results)

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

def query_with_parameters(model_name, order_by=None, page=0, results_per_page=None):
    """
    Input: only input required is Model name
    Output: query according to input query parameters
    """
    query = db.session.query(model_name)
    if order_by:
        query = query.order_by(order_by)
    if results_per_page:
        query = query.limit(results_per_page)
    if page:
        page = int(page) - 1
        query = query.offset(page * int(results_per_page))
    return query

def get_rentals_within_parameters(rentals_list, order_by=None, page=0, results_per_page=None):
    """
    Input: only required input is a list of objects. As this helper function is used, a list of Rental objects.
    Output: A narrowed down list of (Rental) objects that match the given query parameters.
    """
    query = rentals_list
    if order_by:
        query = query.order_by(order_by)
    if results_per_page:
        query = query.limit(results_per_page)
    if page:
        page = int(page) - 1
        query = query.offset(page * int(results_per_page))
    return query
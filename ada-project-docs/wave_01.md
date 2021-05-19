# Wave 1: CRUD for Two Models

## Goal

Our video store API should be able to work with two entities, `Customer` and `Video`.

Customers are entities that describe a customer at the video store.  They contain:

- name of the customer
- postal code of the customer
- phone number of the customer
- register_at datetime of when the customer was added to the system.

Videos are entities that describe a video at the video store.  They contain:

- title of the video
- release date datetime of when the video was release_date
- total inventory of how many copies are owned by the video store

Our goal for this wave is to be able to do all CRUD actions for these two entities.

## Error Handling Requirements for Every Endpoint

It's crucial for all APIs to be able to handle errors. For every required endpoint described in this project, handle errors in this pattern.

If something goes wrong...
- Your API should return an appropriate HTTP status code.
- For POST and PUT requests, responses with 4XX response codes should also return a response body with some indication of what went wrong.


If something goes wrong...
- Your API should return an appropriate HTTP status code.
- For POST and PUT requests, responses with 4XX response codes should also return a response body with some indication of what went wrong.

This could be something as simple as:

```json
{
        "details": "Invalid data"
}
```

...or something slightly more complex like:
```json
[
   "title must be provided and it must be a string",
   "total_inventory must be provided and it must be a number"
]
```

# Requirements

Here we will list every endpoint for these entities.

Every endpoint must serve JSON data, and must use HTTP response codes to indicate the status of the request.

## `/customers` CRUD

Required endpoints:

1. GET `/customers`
1. GET `/customers/<id>`
1. POST `/customers`
1. PUT `/customers/<id>`
1. DELETE `/customers/<id>`

### `GET` `/customers`  details

Lists all existing customers and details about each customer.

#### Required Arguments

No arguments to this request

#### Response

Typical success response:

Status: `200`

```json
[
  {
    "id": 1,
    "name": "Shelley Rocha",
    "registered_at": "Wed, 29 Apr 2015 07:54:14 -0700",
    "postal_code": 24309,
    "phone": "(322) 510-8695",
    "videos_checked_out_count": 0
  },
  {
    "id": 2,
    "name": "Curran Stout",
    "registered_at": "Wed, 16 Apr 2014 21:40:20 -0700",
    "postal_code": 94267,
    "phone": "(908) 949-6758",
    "videos_checked_out_count": 0
  }
]
```

#### Errors & Edge Cases to Check

- The API should return an empty array and a status `200` if there are no customers.

### `GET /customer/<id>`  details
Gives back details about specific customer.

#### Required Arguments

Arg | Type | Details
--- | --- | ---
`id` | integer | The id of the customer

#### Response

Typical success response (these are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
{
    "id": 2,
    "name": "Curran Stout",
    "registered_at": "Wed, 16 Apr 2014 21:40:20 -0700",
    "postal_code": 94267,
    "phone": "(908) 949-6758",
    "videos_checked_out_count": 0
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `404: Not Found` if this customer does not exist.

### `POST /customers` details
Creates a new video with the given params.

#### Required Request Body Parameters

Request Body Param | Type | Details
--- | --- | ---
`name` | string | The name of the customer
`postal_code` | int | The postal code of the customer
`phone` | string | The phone of the customer

#### Response

Typical success response, where `id` is the id of the new customer (this is the minimum required field that the Postman tests will be looking for):

Status: `201: Created`

```json
{
  "id": 10034
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `400: Bad Request` if the customer does not have any of the required fields to be valid.

### `PUT /customer/<id>`  details

Updates and returns details about specific customer.

#### Required Route Arguments

Arg | Type | Details
--- | --- | ---
`id` | integer | The id of the customer

#### Required Request Body Parameters

Request Body Param | Type | Details
--- | --- | ---
`name` | string | The name of the customer
`postal_code` | int | The postal code of the customer
`phone` | string | The phone of the customer

#### Response

Typical success response (these are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
{
    "id": 2,
    "name": "Curran Stout",
    "registered_at": "Wed, 16 Apr 2014 21:40:20 -0700",
    "postal_code": 94267,
    "phone": "(908) 949-6758",
    "videos_checked_out_count": 0
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `404: Not Found` if this customer does not exist.
- The API should return a `400: Bad Request`, if any of the request body fields are missing or invalid.
  - For example if the `name` is an empty string or is not a string.

### `DELETE /customer/<id>`  details
Deletes a specific customer.

#### Required Arguments

Arg | Type | Details
--- | --- | ---
`id` | integer | The id of the customer

#### Response

Typical success response (these are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
{
    "id": 2
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `404: Not Found` if this customer does not exist.

## `/videos` CRUD

Required endpoints:

1. GET `/videos`
1. GET `/vidoes/<id>`
1. POST `/videos`
1. PUT `/videos/<id>`
1. DELETE `/videos/<id>`

## `GET /videos`  details
Lists all existing videos and details about each video.

#### Required Arguments

No arguments to this request

#### Response

Typical success response (this are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
[
  {
    "id": 1,
    "title": "Blacksmith Of The Banished",
    "release_date": "1979-01-18",
    "total_inventory": 10,
    "available_inventory": 9
  },
  {
    "id": 2,
    "title": "Savior Of The Curse",
    "release_date": "2010-11-05",
    "total_inventory": 11,
    "available_inventory": 1
  }
]
```

#### Errors & Edge Cases to Check

- The API should return an empty array and a status `200` if there are no videos.

### `GET /video/<id>`  details
Gives back details about specific video in the store's inventory.

#### Required Arguments

Arg | Type | Details
--- | --- | ---
`id` | integer | The id of the video

#### Response

Typical success response (this are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
{
  "id": 1,
  "title": "Blacksmith Of The Banished",
  "release_date": "1979-01-18",
  "total_inventory": 10,
  "available_inventory": 9
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `404: Not Found` if this video does not exist.

### `POST /videos`  details
Creates a new video with the given params.

#### Required Request Body Parameters

Request Body Param | Type | Details
--- | --- | ---
`title` | string | The title of the video
`release_date` | datetime | Represents the date of the video's release
`total_inventory` | integer | The total quantity of this video in the store

#### Response

Typical success response, where `id` is the id of the new video (this is the minimum required field that the Postman tests will be looking for):

Status: `201: Created`

```json
{
  "id": 277419104
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `400: Bad Request` if the video does not have any of the required fields to be valid.

### `PUT /video/<id>`  details
Gives back details about specific video in the store's inventory.

#### Required Route Arguments

Arg | Type | Details
--- | --- | ---
`id` | integer | The id of the video

#### Required Request Body Parameters

Request Body Param | Type | Details
--- | --- | ---
`title` | string | The title of the video
`release_date` | datetime | Represents the date of the video's release
`total_inventory` | integer | The total quantity of this video in the store


#### Response

Typical success response (this are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
{
  "id": 1,
  "title": "Blacksmith Of The Banished",
  "release_date": "1979-01-18",
  "total_inventory": 10,
  "available_inventory": 9
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `404: Not Found` if this video does not exist.
- The API should return back a `400 Bad Request` response for missing or invalid fields in the request body.
  - For example, if `total_inventory` is missing or is not a number


### `DELETE /video/<id>`  details
Deletes a specific video.

#### Required Arguments

Arg | Type | Details
--- | --- | ---
`id` | integer | The id of the video

#### Response

Typical success response (these are the minimum required fields that the Postman tests will be looking for):

Status: `200`

```json
{
    "id": 12
}
```

#### Errors & Edge Cases to Check

- The API should return back detailed errors and a status `404: Not Found` if this video does not exist.

## Tests

There are no Pytest tests for this project.  There are Postman test scripts for all of these endpoints.  If you want to write your own tests for this project, we recommend using the tests in Task List as a template.

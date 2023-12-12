"""
Wishlist

Describe what your service does here
"""

from flask import jsonify, request, abort, make_response

# from flask_restx import Api, Resource
from flask_restx import fields, reqparse, Resource
from service.common import status  # HTTP Status Codes
from service.models import Wishlist, WishlistItem

# Import Flask application
from . import app, api

# MODELS

create_item_model = api.model(
    "WishlistItem",
    {
        "wishlist_id": fields.Integer(
            required=True, description="The Unique ID of the wishlist for the item"
        ),
        "product_name": fields.String(
            required=True, description="The name of the product in the wishlist"
        ),
        "product_id": fields.Integer(
            required=True, description="The ID of the product in the wishlist"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the product in the wishlist"
        ),
    },
)

item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)


create_wishlist_model = api.model(
    "Wishlist",
    {
        "wishlist_name": fields.String(required=True, description="The Name of the wishlist"),
        "customer_id": fields.Integer(
            required=True, description="The owner id of the wishlist"
        ),
        "is_public": fields.Boolean(
            required=False,
            default=False,
            description="Whether the wishlist is public or not",
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "created_date": fields.Date(
            readOnly=True, description="The day the wishlist was created"
        ),
        "wishlist_items": fields.List(
            fields.Nested(item_model),
            required=False,
            description="The items that the wishlist contains",
        ),
    },
)

# Query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="List Wishlists by name"
)
wishlist_args.add_argument(
    "owner_id",
    type=int,
    location="args",
    required=False,
    help="List Wishlists by Owner ID",
)
wishlist_args.add_argument(
    "product_name",
    type=int,
    location="args",
    required=False,
    help="List Wishlist Items by product name",
)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH
######################################################################
@app.route("/health")
def health():
    """Health endpoint"""
    res = {"status": "OK"}
    return make_response(jsonify(res), status.HTTP_200_OK)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL WISHLISTs
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Returns all of the Wishlists"""
    app.logger.info("Request for Wishlist lists")

    customer_id = request.args.get("customer-id")

    wishlists = []

    if customer_id is not None:
        wishlists = Wishlist.find_by_customer_id(customer_id)
    else:
        wishlists = Wishlist.all()

    # Return as an array of dictionaries
    results = [wishlist.serialize() for wishlist in wishlists]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create an Wishlist based on the data in the body that is posted
    """
    app.logger.info("Request to create an Wishlist")

    # Validate content is json
    check_content_type("application/json")

    # Create the wishlist
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()  # match test case

    return make_response(
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": f"/wishlists/{wishlist.id}"},
    )


######################################################################
#  PATH: /wishlist/{wishlist_id}
######################################################################
@api.route("/wishlists/<wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """
    WishlistResource class

    Allows the manipulation of a single Wishlist
    GET /wishlist{id} - Returns a Wishlist with the id
    PUT /wishlist{id} - Update a Wishlist with the id
    DELETE /wishlist{id} -  Deletes a Wishlist with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlist")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist
        This endpoint will return a Wishlist based on it's id
        """
        app.logger.info("Request to Retrieve a Wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST
    # ------------------------------------------------------------------
    @api.doc("update_wishlists")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    # @token_required
    def put(self, wishlist_id):
        """
        Update an Wishlist
        This endpoint will update an Wishlist based the body that is posted
        """
        app.logger.info("Request to update wishlist with id: %s", wishlist_id)
        check_content_type("application/json")

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        # Update from the json in the body of the request
        wishlist.deserialize(request.get_json())
        wishlist.id = wishlist_id
        # wishlist.name = newname
        wishlist.update()

        return wishlist.serialize(), status.HTTP_200_OK

######################################################################
#  PATH: /wishlists
######################################################################
@api.route("/wishlists", strict_slashes=False)
class WishlistsCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    # ------------------------------------------------------------------
    # ADD A NEW WISHLISTS
    # ------------------------------------------------------------------
    @api.doc("create_wishlists")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist
        This endpoint will create a Wishlist based the data in the body that is posted
        """
        app.logger.info("Request to Create a Wishlist")
        wishlist = Wishlist()
        app.logger.debug("Payload = %s", api.payload)
        wishlist.deserialize(api.payload)
        wishlist.create()
        app.logger.info("Pet with new id [%s] created!", wishlist.id)
        location_url = api.url_for(WishlistResource, pet_id=wishlist.id, _external=True)
        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


# ######################################################################
# # READ A WISHLIST
# ######################################################################
# @app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
# def read_wishlists(wishlist_id):
#     """
#     Reads an Existing Wishlist
#     This endpoint will read a Wishlist based on the given id
#     """
#     app.logger.info("Request to read Wishlist: %d", wishlist_id)

#     # Check if wishlist exists
#     wishlist = Wishlist.find(wishlist_id)
#     if not wishlist:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Wishlist with id '{wishlist_id}' could not be found.",
#         )
#     return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE A WISHLIST
######################################################################
# @app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
# def update_wishlists_by_name(wishlist_id):
#     """
#     Update an Wishlist
#     This endpoint will update an Wishlist based the body that is posted
#     """
#     app.logger.info("Request to update wishlist with id: %s", wishlist_id)
#     check_content_type("application/json")

#     # See if the wishlist exists and abort if it doesn't
#     wishlist = Wishlist.find(wishlist_id)
#     if not wishlist:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Wishlist with id '{wishlist_id}' was not found.",
#         )
#     # Update from the json in the body of the request
#     wishlist.deserialize(request.get_json())
#     wishlist.id = wishlist_id
#     # wishlist.name = newname
#     wishlist.update()

#     return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", wishlist_id)

    # Retrieve the account to delete and delete it if it exists
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# PUBLISH A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/publish", methods=["PUT"])
def publish_wishlist(wishlist_id):
    """
    Publish a wishlist
    """
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )
    # Update from the json in the body of the request
    wishlist.is_public = True
    wishlist.update()

    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


# ---------------------------------------------------------------------
#                W I S H L I S T   I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# CREATE A NEW WISHLIST ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def create_wishlist_item(wishlist_id):
    """
    Creates a Wishlist Item and associates it with a specific Wishlist
    This endpoint will create a Wishlist Item based on the data in the request body
    and associate it with the specified Wishlist.
    """
    app.logger.info("Request to create a Wishlist Item")

    # Validate content is JSON
    check_content_type("application/json")

    # Find the specified Wishlist
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with ID {wishlist_id} not found")

    # Create the Wishlist Item
    wishlist_item = WishlistItem()
    wishlist_item.deserialize(request.get_json())
    wishlist_item.wishlist_id = (
        wishlist.id
    )  # Associate the item with the specified wishlist

    # Append items to the wishlist
    wishlist.items.append(wishlist_item)
    wishlist.update()

    # Create a message to return
    message = wishlist_item.serialize()

    return make_response(
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": f"/wishlists/{wishlist.id}/items/{wishlist_item.id}"},
    )


######################################################################
# LIST ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_wishlist_items(wishlist_id):
    """Returns wishlist items based on query parameters"""
    app.logger.info(
        "Request for all WishlistItems for Wishlist with id: %s", wishlist_id
    )

    # See if the account exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    query_params = request.args.to_dict()

    # Initialize base query for items related to this wishlist
    base_query = WishlistItem.query.filter_by(wishlist_id=wishlist_id)

    # Check for query parameters and filter the base query accordingly
    if "product_id" in query_params:
        base_query = base_query.filter_by(product_id=query_params["product_id"])

    if "product_name" in query_params:
        base_query = base_query.filter(
            WishlistItem.product_name.ilike(f"%{query_params['product_name']}%")
        )

    if "product_price" in query_params:
        base_query = base_query.filter(
            WishlistItem.product_price <= query_params["product_price"]
        )

    if "quantity" in query_params:
        base_query = base_query.filter(
            WishlistItem.quantity <= query_params["quantity"]
        )

    if "created_date" in query_params:
        base_query = base_query.filter_by(created_date=query_params["created_date"])

    # Fetch the filtered results
    results = [item.serialize() for item in base_query.all()]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# DELETE ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_addresses(wishlist_id, item_id):
    """
    Delete an Item

    This endpoint will delete an Item based the id specified in the path
    """

    app.logger.info(
        "Request to delete Item %s for Wishlist id: %s", item_id, wishlist_id
    )

    # Find the specified Wishlist
    wishlist = Wishlist.find(wishlist_id)

    # Find the specified WishlistItem
    if wishlist:
        wishlist_item = None
        for item in wishlist.items:
            if item.id == item_id:
                wishlist_item = item
                break

        wishlist_item.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# READ ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["GET"])
def read_wishlist_item(wishlist_id, item_id):
    """
    Reads an Item from existing Wishlist
    This endpoint will read an Item from a Wishlist based on the given id
    """
    app.logger.info("Request to read item: %d from Wishlist: %d", item_id, wishlist_id)

    # Check if wishlist exists
    item = WishlistItem.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in Wishlist with id '{wishlist_id}' could not be found.",
        )
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_wishlist_items(wishlist_id, item_id):
    """Update a wishlist item"""
    app.logger.info(
        "Request to update Item %s for Wishlist id: %s", item_id, wishlist_id
    )

    # Validate content is JSON
    check_content_type("application/json")

    # Find the specified Wishlist
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with ID {wishlist_id} not found")

    # Find the specified WishlistItem
    wishlist_item = None
    for item in wishlist.items:
        if item.id == item_id:
            wishlist_item = item
            break

    if not wishlist_item:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist Item with ID {item_id} not found")

    wishlist_item.deserialize(request.get_json())
    wishlist_item.id = item_id
    wishlist_item.update()

    return make_response(
        jsonify(wishlist_item.serialize()),
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )

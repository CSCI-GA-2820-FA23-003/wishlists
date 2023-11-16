"""
Wishlist

Describe what your service does here
"""

from flask import jsonify, request, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Wishlist, WishlistItem

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""

    return (
        jsonify(
            {
                "resources": {
                    "wishlists": {
                        "url": "/wishlists",
                        "subResources": {"items": {"url": "{wishlist_id}/items"}},
                    }
                }
            }
        ),
        status.HTTP_200_OK,
    )


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
# READ A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def read_wishlists(wishlist_id):
    """
    Reads an Existing Wishlist
    This endpoint will read a Wishlist based on the given id
    """
    app.logger.info("Request to read Wishlist: %d", wishlist_id)

    # Check if wishlist exists
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlists_by_name(wishlist_id):
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

    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


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
    """Returns all of the Items for a Wishlist"""
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

    # Get the items for the wishlist
    results = [item.serialize() for item in wishlist.items]

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

    # See if the address exists and delete it if it does
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

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

    # Update the Quantity of the WishlistItem
    data = request.get_json()
    if "quantity" in data:
        wishlist_item.quantity = data["quantity"]
        wishlist.update()

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

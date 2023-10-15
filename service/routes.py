"""
Wishlist

Describe what your service does here
"""

from flask import jsonify, request, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Wishlist

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...


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

@app.route("/wishlists/<int:id>", methods=["GET"])
def read_wishlists(id):
    """
    Reads an Existing Wishlist
    This endpoint will read a Wishlist based on the given id
    """
    app.logger.info(f"Request to read Wishlist: {id}")

    # Validate content is json
    check_content_type("application/json")

    # Check if wishlist exists
    wishlist = Wishlist.find(id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{id}' could not be found."
        )
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)
   


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
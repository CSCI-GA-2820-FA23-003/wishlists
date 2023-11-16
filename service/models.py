"""
Models for Wishlist

All of the models are stored in this module
"""
import logging
from datetime import date
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Wishlist.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """
    Base class for persistent models
    """

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self):
        """
        Creates a Wishlist to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # pylint: disable=invalid-name
        # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Wishlist to the database
        """
        logger.info("Updating %s", self.id)
        db.session.commit()

    def delete(self):
        """Removes a Wishlist from the data store"""
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the Wishlists in the database"""
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Wishlist by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  W I S H L I S T   M O D E L
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a Wishlist
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    is_public = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.Integer)
    wishlist_name = db.Column(db.String(64))  # e.g., work, home, vacation, etc.
    created_date = db.Column(db.Date(), nullable=False, default=date.today())
    items = db.relationship("WishlistItem", backref="wishlist", passive_deletes=True)

    def __repr__(self):
        return f"<wishlist_id=[{self.id}]>"

    def serialize(self):
        """Converts an Wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "customer_id": self.customer_id,
            "wishlist_name": self.wishlist_name,
            "created_date": self.created_date.isoformat(),
            "is_public" : self.is_public,

        }
        return wishlist

    def deserialize(self, data):
        """
        Populates an Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.wishlist_name = data["wishlist_name"]
            self.created_date = date.fromisoformat(data["created_date"])
            self.is_public = data.get("is_public", False)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_customer_id(cls, customer_id: int) -> list:
        """Returns all wishlists for a given customer id

        :param customer_id: customer id of customer who owns the list
        :type customer_id: int

        :return: a collection of wishlists (or empty list)
        :rtype: list

        """
        logger.info("Querying wishlists for customer id: [%s]", customer_id)
        return cls.query.filter(cls.customer_id == customer_id).all()
    
    @app.route('/wishlists/<int:wishlist_id>/publish', methods=['PUT'])
    def publish_wishlist(wishlist_id):
        """
        Publish a wishlist
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

        wishlist.is_public = True
        wishlist.update()

        return jsonify(wishlist.serialize()), 200



######################################################################
# WISHLIST ITEM MODEL
######################################################################
class WishlistItem(db.Model, PersistentBase):
    """Models an item within a Wishlist"""

    __tablename__ = "wishlist_items"

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(
        db.Integer,
        db.ForeignKey("wishlist.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(255))
    product_price = db.Column(db.Numeric)
    quantity = db.Column(db.Integer)
    created_date = db.Column(db.Date(), nullable=False, default=date.today())

    def __repr__(self):
        return (
            f"WishlistItem("
            f"id={self.id}, "
            f"wishlist_id={self.wishlist_id}, "
            f"product_id={self.product_id}, "
            f"product_name='{self.product_name}', "
            f"product_price={self.product_price}, "
            f"quantity={self.quantity}, "
            f"created_date='{self.created_date.isoformat()}'"
            f")"
        )

    def serialize(self):
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_price": self.product_price,
            "quantity": self.quantity,
            "created_date": self.created_date.isoformat(),
        }

    def deserialize(self, data: dict):
        try:
            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.product_name = data["product_name"]
            self.product_price = data["product_price"]
            self.quantity = data["quantity"]
            self.created_date = date.fromisoformat(data["created_date"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist Item: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

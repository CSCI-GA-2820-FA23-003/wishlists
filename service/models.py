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
    """ Initializes the SQLAlchemy app """
    Wishlist.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


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
        logger.info("Creating %s", self.wishlist_id)
        self.id = None  # pylint: disable=invalid-name
        # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Wishlist to the database
        """
        logger.info("Saving %s", self.wishlist_id)
        db.session.commit()

    def delete(self):
        """ Removes a Wishlist from the data store """
        logger.info("Deleting %s", self.wishlist_id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Wishlists in the database """
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Wishlist by it's ID """
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
    wishlist_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    wishlist_name = db.Column(db.String(64))  # e.g., work, home, vacation, etc.
    created_date = db.Column(db.Date(), nullable=False, default=date.today())

    def __repr__(self):
        return f"<Wishlist id=[{self.id}]>"
    
    def serialize(self):
        """Converts an Wishlist into a dictionary"""
        wishlist = {
            "wishlist_id": self.wishlist_id,
            "customer_id": self.customer_id,
            "wishlist_name": self.wishlist_name,
            "created_date": self.created_date.isoformat(),
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
            except KeyError as error:
                raise DataValidationError("Invalid Wishlist: missing " + error.args[0]) from error
            except TypeError as error:
                raise DataValidationError(
                    "Invalid Wishlist: body of request contained "
                    "bad or no data - " + error.args[0]
                ) from error
            return self
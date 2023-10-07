"""
Test cases for Wishlist Model

"""
import os
import logging
import unittest
from service import app
from service.models import Wishlist, DataValidationError, db
from tests.factories import WishlistFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  Wishlist   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(unittest.TestCase):
    """ Test Cases for Wishlist Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Wishlist.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def setUp(self):
        """ This runs before each test """

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should Create a Wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            customer_id=fake_wishlist.customer_id,
            created_date=fake_wishlist.created_date,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.wishlist_id, None)
        self.assertEqual(wishlist.customer_id, fake_wishlist.customer_id)
        self.assertEqual(wishlist.created_date, fake_wishlist.created_date)

    def test_add_a_wishlist(self):
        """It should Create a Wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.wishlist_id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    def test_read_wishlist(self):
        """It should Read an wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Read it back
        found_wishlist = Wishlist.find(wishlist.wishlist_id)
        self.assertEqual(found_wishlist.wishlist_id, wishlist.wishlist_id)
        self.assertEqual(found_wishlist.customer_id, wishlist.customer_id)
        self.assertEqual(found_wishlist.created_date, wishlist.created_date)

    

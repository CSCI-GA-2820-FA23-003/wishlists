"""
Wishlist API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import WishlistFactory, WishlistItemFactory
from service import app
from service.models import db, Wishlist, init_db
from service.common import status  # HTTP Status Codes

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistServer(TestCase):
    """Wishlist REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.query(Wishlist).delete()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################
    def _create_wishlists(self, count):
        """Wishlist method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Wishlist",
            )
            new_account = resp.get_json()
            wishlist.id = new_account["id"]
            wishlist.customer_id = new_account["customer_id"]
            wishlist.wishlist_name = new_account["wishlist_name"]
            wishlist.created_date = new_account["created_date"]
            wishlists.append(wishlist)
        return wishlists

    ######################################################################
    #  W I S H L I S T   T E S T   C A S E S   H E R E
    ######################################################################
    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_wishlist(self):
        """It should Create a new Wishlist"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set (part of RESTful api definition)
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct (response from db)
        new_wishlist = resp.get_json()
        self.assertEqual(
            new_wishlist["wishlist_name"],
            wishlist.wishlist_name,
            "Wishlist names does not match",
        )
        self.assertEqual(
            new_wishlist["created_date"],
            str(wishlist.created_date),
            "Created Date does not match",
        )

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"wishlist_name": "my wishlist"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_wishlist(self):
        """It checks if the GET Method to read a wishlist works"""
        wishlist = self._create_wishlists(1)[0]
        wishlist_id = wishlist.id
        customer_id = wishlist.customer_id
        wishlist_name = wishlist.wishlist_name
        created_date = str(
            wishlist.created_date
        )  # convert datetime object to string since resp will be in json
        resp = self.client.get(
            f"{BASE_URL}/{wishlist_id}", content_type="application/json"
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data["id"], wishlist_id)
        self.assertEqual(data["customer_id"], customer_id)
        self.assertEqual(data["wishlist_name"], wishlist_name)
        self.assertEqual(data["created_date"], str(created_date))

    def test_delete_wishlist(self):
        """It should Delete a Wishlist"""
        # get the id of a wishlist
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_sad_path_wishlist(self):
        """It should throw an error code"""
        # get the id of a wishlist
        wishlist = self._create_wishlists(1)
        max_wishlist_id = -1
        for i in wishlist:
            max_wishlist_id = max(max_wishlist_id, i.id)
        resp = self.client.delete(f"{BASE_URL}/{max_wishlist_id+1}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wishlist_not_found(self):
        """It should not Read an Wishlist that is not found"""
        resp = self.client.get(f"{BASE_URL}/0", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIsNotNone(resp.get_json())

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_wishlist_list(self):
        """It should Get a list of Wishlists"""
        wishlist = self._create_wishlists(5)
        wishlist_array = []
        for itr in wishlist:
            wishlist_id = itr.id
            customer_id = itr.customer_id
            wishlist_name = itr.wishlist_name
            created_date = itr.created_date
            wishlist_array.append(
                {
                    "id": wishlist_id,
                    "customer_id": customer_id,
                    "wishlist_name": wishlist_name,
                    "created_date": created_date,
                }
            )
        resp = self.client.get(BASE_URL, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)
        self.assertEqual(data, wishlist_array)

    ######################################################################
    #  W I S H L I S T   I T E M   T E S T   C A S E S   H E R E
    ######################################################################
    def test_create_wishlist_item(self):
        """It should create a new Wishlist Item and associate it with a specific Wishlist"""
        # Create a Wishlist to associate the item with
        wishlist = self._create_wishlists(1)[0]

        # Confirm that wishlist.id is not None
        self.assertIsNotNone(wishlist.id)

        # Create a Wishlist Item
        wishlist_item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Ensure that the Location header is set and matches the expected URL
        expected_location = f"{BASE_URL}/{wishlist.id}/items/{wishlist_item.id}"
        self.assertEqual(resp.headers["Location"], expected_location)

        # Make sure location header is set (part of RESTful api definition)
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct (response from db)
        data = resp.get_json()

        self.assertEqual(
            data["wishlist_id"],
            wishlist.id,
            "Wishlist Item is not associated with the correct Wishlist",
        )
        self.assertEqual(
            data["product_id"],
            wishlist_item.product_id,
            "Product Id does not match",
        )
        self.assertEqual(
            data["product_name"],
            wishlist_item.product_name,
            "Product Name does not match",
        )
        self.assertEqual(
            data["product_price"],
            str(wishlist_item.product_price),
            "Product Price does not match",
        )
        self.assertEqual(
            data["quantity"],
            wishlist_item.quantity,
            "Quantity does not match",
        )
        self.assertEqual(
            # datetime.strptime(new_wishlist_item["created_date"], '%a, %d %b %Y %H:%M:%S GMT').date(),
            data["created_date"],
            str(wishlist_item.created_date),
            "Created Date does not match",
        )

    def test_create_wishlist_item_bad_request(self):
        """It should not create a Wishlist Item when sending the wrong data"""
        wishlist = WishlistFactory()
        resp_wishlist = self.client.post(BASE_URL, json=wishlist.serialize())
        self.assertEqual(resp_wishlist.status_code, status.HTTP_201_CREATED)
        wishlist_data = resp_wishlist.get_json()

        # Attempt to create a Wishlist Item with incomplete data
        resp = self.client.post(
            f'{BASE_URL}/{wishlist_data["id"]}/items',
            json={"item_property": "Example Property"},  # Incomplete data
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_item_not_found(self):
        """It should not create a Wishlist Item for a Wishlist that is not found"""
        resp = self.client.post(
            f"{BASE_URL}/0/items",
            json={"item_property": "Example Property"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist_item_unsupported_media_type(self):
        """It should not create a Wishlist Item when sending the wrong media type"""
        wishlist = WishlistFactory()
        resp_wishlist = self.client.post(BASE_URL, json=wishlist.serialize())
        self.assertEqual(resp_wishlist.status_code, status.HTTP_201_CREATED)
        wishlist_data = resp_wishlist.get_json()

        # Attempt to create a Wishlist Item with the wrong media type
        resp = self.client.post(
            f'{BASE_URL}/{wishlist_data["id"]}/items',
            json={"item_property": "Example Property"},
            content_type="test/html",  # Incorrect media type
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIsNotNone(resp.get_json())

    def test_get_wishlist_item_list(self):
        """It should Get a list of items"""
        # add two items to wishlist
        wishlist = WishlistFactory()
        items = WishlistItemFactory.create_batch(2)

        wishlist.items.extend(items)

        wishlist.create()

        self.assertIsNotNone(wishlist.id)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

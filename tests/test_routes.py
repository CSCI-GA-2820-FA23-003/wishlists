"""
Wishlist API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import WishlistFactory
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

    def test_update_a_wishlist(self):
        """It should update a Wishlist"""
        wishlist1 = WishlistFactory()
        wishlist2 = WishlistFactory()
        res = self.client.post(
            BASE_URL, json=wishlist1.serialize(), content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data1 = res.get_json()
        res = self.client.post(
            BASE_URL, json=wishlist2.serialize(), content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data2 = res.get_json()
        # Attempt to rename both to the same name
        wishlist1.wishlist_name = "new_Name"
        wishlist2.wishlist_name = "new_Name"
        res1 = self.client.put(
            f"{BASE_URL}/{data1['id']}",
            json=wishlist1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(
            res1.status_code, status.HTTP_200_OK, "Could not rename Wishlist1"
        )
        res2 = self.client.put(
            f"{BASE_URL}/{data2['id']}",
            json=wishlist2.serialize(),
            content_type="application/json",
        )
        self.assertEqual(
            res2.status_code, status.HTTP_409_CONFLICT, "Incorrectly renamed Wishlist2"
        )
        # Verify the updated data
        wl1 = Wishlist.find(data1["id"]).wishlist_name
        wl2 = Wishlist.find(data2["id"]).wishlist_name
        self.assertEqual(wl1, "new_Name")
        self.assertNotEqual(wl2, "new_Name")

    def test_cannot_update_a_wishlist(self):
        """It should fail to update a Wishlist when it doesn't exist or the desired name already exists"""
        created_wishlists = self._create_wishlists(2)
        created_wishlist_ids = [wishlist.id for wishlist in created_wishlists]
        # Picking a non-existent wishlist id
        non_existent_wishlist_id = created_wishlist_ids[0]
        while non_existent_wishlist_id in created_wishlist_ids:
            non_existent_wishlist_id += 1
        # Attempting to update a non-existent wishlist
        wishlist = WishlistFactory()
        resp = self.client.put(
            f"{BASE_URL}/{non_existent_wishlist_id}",
            json=wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # Attempting to rename a wishlist with an already-consumed name
        wishlist.wishlist_name = created_wishlists[0].wishlist_name
        resp = self.client.put(
            f"{BASE_URL}/{created_wishlist_ids[1]}",
            json=wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

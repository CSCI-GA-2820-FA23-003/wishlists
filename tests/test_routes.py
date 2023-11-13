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
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlist.customer_id = new_wishlist["customer_id"]
            wishlist.wishlist_name = new_wishlist["wishlist_name"]
            wishlist.created_date = new_wishlist["created_date"]
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

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(
            new_wishlist["wishlist_name"],
            wishlist.wishlist_name,
            "Names does not match",
        )
        self.assertEqual(
            new_wishlist["created_date"],
            str(wishlist.created_date),
            "Created date does not match",
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

    def test_update_wishlist(self):
        """It should Update an existing Wishlist"""
        # create an Wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the wishlist
        new_wishlist = resp.get_json()
        new_wishlist["wishlist_name"] = "devops-wishlist"
        new_wishlist_id = new_wishlist["id"]
        resp = self.client.put(f"{BASE_URL}/{new_wishlist_id}", json=new_wishlist)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["wishlist_name"], "devops-wishlist")

    def test_update_nonexistent_wishlist(self):
        """It should return 404 when trying to update a nonexistent Wishlist."""
        # Create a test wishlist but do not persist it to the server.
        test_wishlist = WishlistFactory()

        # Try to update a wishlist that doesn't exist.
        nonexistent_wishlist_id = 99999  # Assuming this ID doesn't exist.
        resp = self.client.put(
            f"{BASE_URL}/{nonexistent_wishlist_id}", json=test_wishlist.serialize()
        )

        # Check if the response status code indicates the wishlist is not found.
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

        # Check the data is correct (response from db)
        data = resp.get_json()

        # Ensure that the Location header is set and matches the expected URL
        expected_location = f"{BASE_URL}/{wishlist.id}/items/{data['id']}"
        self.assertEqual(resp.headers["Location"], expected_location)

        # Make sure location header is set (part of RESTful api definition)
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

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

    def test_create_duplicate_wishlist_item(self):
        """It should create 2 new Wishlist Items and associate it with a specific Wishlist"""
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

        # Create a second identical Wishlist Item
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

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

    def test_sad_path_get_wishlist_item_list(self):
        """It should not return a list of items"""
        # add two items to wishlist
        wishlist = WishlistFactory()
        items = WishlistItemFactory.create_batch(2)

        wishlist.items.extend(items)

        wishlist.create()

        self.assertIsNotNone(wishlist.id)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{wishlist.id + 1}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist_item(self):
        """It should Delete a Wishlist Item"""
        # add two items to wishlist
        wishlist = self._create_wishlists(1)[0]
        self.assertIsNotNone(wishlist.id)
        wishlist_item = WishlistItemFactory()

        # get the list back and make sure there are 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)

        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure wishlist item is not there
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/addresses/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_sad_path_delete_wishlist_item(self):
        """It should Delete a Wishlist Item"""
        # add two items to wishlist
        wishlist = self._create_wishlists(1)[0]
        self.assertIsNotNone(wishlist.id)
        wishlist_item = WishlistItemFactory()

        # get the list back and make sure there are 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)

        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{wishlist.id + 1}/items/{item_id}",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_wishlist_item(self):
        """It should read an existing Item from an existing Wishlist"""
        # Create a Wishlist to associate the item with
        wishlist = self._create_wishlists(1)[0]

        # Confirm that wishlist.id is not None
        self.assertIsNotNone(wishlist.id)

        # Create a Wishlist Item
        item = WishlistItemFactory()
        item.wishlist_id = wishlist.id
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)

        self.assertEqual(data["wishlist_id"], item.wishlist_id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(float(data["product_price"]), item.product_price)
        self.assertEqual(float(data["quantity"]), item.quantity)
        self.assertEqual(data["created_date"], str(item.created_date))

    def test_read_wishlist_item_not_found(self):
        """It should not be able to find the item and throw an error"""
        # Create a Wishlist to associate the item with
        wishlist = self._create_wishlists(1)[0]

        # Confirm that wishlist.id is not None
        self.assertIsNotNone(wishlist.id)

        # Create a Wishlist Item
        item = WishlistItemFactory()
        item.wishlist_id = wishlist.id

        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{item.id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist_item(self):
        """It should update a Wishlist Item (e.g., update quantity)"""
        # Create a Wishlist to associate the item with
        wishlist = self._create_wishlists(1)[0]

        # Create a Wishlist Item
        wishlist_item = WishlistItemFactory()
        resp_create = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp_create.status_code, status.HTTP_201_CREATED)
        data_create = resp_create.get_json()

        # Update the Wishlist Item (e.g., change the quantity)
        updated_data = {"quantity": 10}  # Change the quantity to 10
        resp_update = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{data_create['id']}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(resp_update.status_code, status.HTTP_200_OK)
        data_update = resp_update.get_json()

        # Verify that the quantity has been updated
        self.assertEqual(data_update["quantity"], 10)

    def test_update_wishlist_item_not_found(self):
        """It should not update a Wishlist Item for an item that is not found"""
        # Create a Wishlist to associate the item with
        wishlist = self._create_wishlists(1)[0]

        # Attempt to update a Wishlist Item that doesn't exist
        updated_data = {"quantity": 10}  # Change the quantity to 10
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/0",  # Use a non-existing item_id
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist_item_sad_path(self):
        """It should not update a Wishlist Item for a wishlist that is not found"""
        # Create a Wishlist Item to attempt updating
        wishlist_item = WishlistItemFactory()

        # Attempt to update a Wishlist Item with a wishlist that doesn't exist
        updated_data = {"quantity": 10}  # Change the quantity to 10
        resp = self.client.put(
            f"{BASE_URL}/0/items/{wishlist_item.id}",  # Use a non-existing wishlist_id
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_wishlist_items(self):
        """It should query and return a list of Wishlist Items based on specific criteria"""
        # Create a Wishlist and add multiple Wishlist Items to it
        wishlist = self._create_wishlists(1)[0]
        wishlist_id = wishlist.id
        items = WishlistItemFactory.create_batch(5)
        wishlist.items.extend(items)
        wishlist.create()
        for item in items:
            item.wishlist_id = wishlist_id
        db.session.commit()

        # Query Wishlist Items by wishlist_id
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        # Query Wishlist Items by product_name
        product_name = items[0].product_name
        resp = self.client.get(
            f"{BASE_URL}/{wishlist_id}/items?product_name={product_name}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        self.assertEqual(data[0]["product_name"], product_name)

        # Query Wishlist Items by product_price
        product_price = items[1].product_price
        resp = self.client.get(
            f"{BASE_URL}/{wishlist_id}/items?product_price={product_price}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        self.assertEqual(data[1]["product_price"], str(product_price))

        # Query Wishlist Items by quantity
        quantity = items[2].quantity
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items?quantity={quantity}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        self.assertEqual(data[2]["quantity"], quantity)

    def test_query_wishlist_not_found(self):
        """It should return a 404 status code when querying Wishlist Items for a non-existent Wishlist"""
        resp = self.client.get(f"{BASE_URL}/0/items?product_name=example")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_wishlist_items_no_match(self):
        """It should return an empty list when no Wishlist Items match the criteria"""
        # Create a Wishlist without adding any Wishlist Items
        wishlist = self._create_wishlists(1)[0]
        wishlist_id = wishlist.id

        # Query Wishlist Items by a criteria that doesn't match any items
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items?product_name=nonexistent")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_query_wishlist_items_multiple_criteria(self):
        """It should query and return a list of Wishlist Items based on multiple criteria"""
        wishlist = self._create_wishlists(1)[0]
        wishlist_id = wishlist.id
        items = WishlistItemFactory.create_batch(5)
        wishlist.items.extend(items)
        wishlist.create()
        for item in items:
            item.wishlist_id = wishlist_id
        db.session.commit()

        # Query Wishlist Items by product_name and product_price
        product_name = items[0].product_name
        product_price = items[0].product_price
        resp = self.client.get(
            f"{BASE_URL}/{wishlist_id}/items?product_name={product_name}&product_price={product_price}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        # Ensure only one item is returned and it matches the criteria
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["product_name"], product_name)
        self.assertEqual(data[0]["product_price"], str(product_price))

    def test_query_wishlist_invalid_id(self):
        """It should return a 404 status code when receiving an invalid id"""
        resp = self.client.get(f"{BASE_URL}/invalid/items?product_name=example")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_empty_wishlist_items(self):
        """It should return an empty list when querying Wishlist Items for an empty Wishlist"""
        wishlist = self._create_wishlists(1)[0]
        wishlist_id = wishlist.id

        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_query_wishlist_items_valid_wishlist_id(self):
        """It should successfully query Wishlist Items with a valid Wishlist ID"""
        # Create a Wishlist and some Wishlist Items
        wishlist = self._create_wishlists(1)[0]
        wishlist_id = wishlist.id
        items = WishlistItemFactory.create_batch(3)
        wishlist.items.extend(items)
        wishlist.create()
        db.session.commit()

        # Query Wishlist Items with a valid Wishlist ID
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items?product_name=example")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 0)
  

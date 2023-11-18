"""
WishlistItem Steps

Steps file for wishlist_items.feature
"""

import requests

# for some reason pylint flags this import as E0611 - no-name-in-module
# despite the fact that it is there and functions as expected, so adding this 
# disable to avoid linter false positives
# pylint: disable=E0611
from behave import when

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@when("hello wishlist item world")
def step_impl(context):
    """Stubbing out first wishlist item test"""
    print("hello BDD world!")

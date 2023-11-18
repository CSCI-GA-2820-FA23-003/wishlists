"""
Wishlist Steps

Steps file for wishlists.feature
"""

import requests

# for some reason pylint flags this import as E0611 - no-name-in-module
# despite the fact that it is there and functions as expected, so adding this 
# disable to avoid linter false positives
# pylint: disable=E0611
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("hello world")
def step_impl(context):
    """Stubbing out first test"""
    print("hello BDD world!")

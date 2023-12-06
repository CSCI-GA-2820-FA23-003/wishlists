"""
Wishlist Steps

Steps file for wishlists.feature
"""

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# for some reason pylint flags this import as E0611 - no-name-in-module
# despite the fact that it is there and functions as expected, so adding this
# disable to avoid linter false positives
# pylint: disable=E0611
from behave import when, given, then

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


# this is only if we need to create db items to work on it is the equivalent of
# pet_steps.py here: https://github.com/nyu-devops/lab-flask-bdd/blob/master/features/steps/pets_steps.py


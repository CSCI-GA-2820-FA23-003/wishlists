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
@when('I visit the "home page"')
def step_impl(context):
    context.driver.get(context.base_url)

@when('I set the "Customer ID" to "{customer_id}"')
def step_set_customer_id(context, customer_id):
    customer_id_element = context.driver.find_element(By.ID, "wishlist_customer_id")
    customer_id_element.clear()
    customer_id_element.send_keys(customer_id)

@when('I press the "{button_name}" button')
def step_press_button(context, button_name):
    button = context.driver.find_element(By.ID, f"{button_name.lower()}-btn")
    button.click()

@then('I should see the message "{message}"')
def step_see_message(context, message):
    flash_message = context.driver.find_element(By.ID, "flash_message")
    assert message in flash_message.text

@then('I should see "{text}" in the "{field_name}" field')
def step_see_text_in_field(context, text, field_name):
    field = context.driver.find_element(By.ID, field_name.lower())
    assert text in field.get_attribute("value")

@when('I change "{field_name}" to "{new_text}"')
def step_change_field_text(context, field_name, new_text):
    field = context.driver.find_element(By.ID, field_name.lower())
    field.clear()
    field.send_keys(new_text)

@when('I copy the "{field_name}" field')
def step_copy_field(context, field_name):
    field = context.driver.find_element(By.ID, field_name.lower())
    context.copied_value = field.get_attribute("value")

@when('I paste the "{field_name}" field')
def step_paste_field(context, field_name):
    field = context.driver.find_element(By.ID, field_name.lower())
    field.clear()
    field.send_keys(context.copied_value)

@then('I should not see "{text}" in the results')
def step_should_not_see_in_results(context, text):
    results = context.driver.find_element(By.ID, "search_results").text
    assert text not in results

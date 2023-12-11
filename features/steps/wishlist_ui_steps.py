# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web UI Steps

Steps file for web interactions with Selenium
"""
import logging

# for some reason pylint flags this import as E0611 - no-name-in-module
# despite the fact that it is there and functions as expected, so adding this
# disable to avoid linter false positives
# pylint: disable=E0611
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "wishlist_"


@when('I visit the "Admin UI Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert (
        message in context.driver.title
    ), f"'{message}' does not match '{context.driver.title}'"


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I check the "{element_name}" checkbox')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    checkbox = context.driver.find_element(By.ID, element_id)
    if not checkbox.is_selected():
        checkbox.click()
    context.driver.save_screenshot("home_page.png")


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    assert(found)


@then('"{element_name}" should "{be_or_not_be}" checked')
def step_impl(context, element_name, be_or_not_be):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    checkbox = context.driver.find_element(By.ID, element_id)
    be_or_not_be = be_or_not_be.lower()
    if be_or_not_be == "be":
        assert checkbox.is_selected()
    elif be_or_not_be == "not be":
        assert not checkbox.is_selected()
    else:
        raise ValueError(f'Invalid value for "be_or_not_be": {be_or_not_be}') 


@when('I change "{element_name}" to "{new_text}"')
def step_impl(context, element_name, new_text):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(new_text)
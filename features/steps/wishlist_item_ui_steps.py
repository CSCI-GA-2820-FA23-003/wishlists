# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Wishlist Item UI Steps

Steps file for web interactions with Selenium
"""
# import logging

# for some reason pylint flags this import as E0611 - no-name-in-module
# despite the fact that it is there and functions as expected, so adding this
# disable to avoid linter false positives
# pylint: disable=E0611
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "item_"


@then("The wishlist_id should match in both forms")
def step_impl(context):
    """Explicitly check that the wishlist_id field matches the item_id field"""
    wishlist_id_element = context.driver.find_element(By.ID, "wishlist_id")
    item_id_element = context.driver.find_element(By.ID, "item_id")
    assert wishlist_id_element.text == item_id_element.text


# this differs from the similar when-
# clause from wishlist_ui by the inclusion of 'item' in the sentence
# i.e. I set the "element" to "value" versus I set the **item** "element to "value"
@when('I set the item "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    """Set field values on the item form"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@then('The item "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value((By.ID, element_id), "")
    )
    assert found


@when('I press the item "{button}" button')
def step_impl(context, button):
    button_id = "item-" + button.lower() + "-btn"
    context.driver.find_element(By.ID, button_id).click()
    # context.driver.save_screenshot('home_page.png')


# note XPath is 1 based!
@when('I click the "{button}" button in the item table row "{row_index}"')
def step_impl(context, button, row_index):
    edit_button_locator = (
        By.XPATH,
        "//table[@id='wishlist-items-table']//tbody/tr["
        + row_index
        + "]//button[contains(@class, 'item-"
        + button.lower()
        + "-btn')]",
    )
    edit_button = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located(edit_button_locator)
    )
    edit_button.click()


@then('I should see "{text_string}" in the item "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found

@then('I should see the message item "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found

@when('I copy the item "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")

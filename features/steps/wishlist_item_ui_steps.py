# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Wishlist Item UI Steps

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
from selenium.common.exceptions import TimeoutException

ID_PREFIX = "item_"


@then("The wishlist_id should match in both forms")
def step_impl(context):
    """Explicitly check that the wishlist_id field matches the item_id field"""
    wishlist_id_element = context.driver.find_element(By.ID, "wishlist_id")
    item_id_element = context.driver.find_element(By.ID, "item_id")
    assert wishlist_id_element.text == item_id_element.text


# this differs from the similar when clause from wishlist_ui by the inclusion of 'item' in the sentence
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


@then('I should see "{expected_rows}" rows in the table "{table_id}"')
def step_impl(context, expected_rows, table_id):
    table_selector = "#" + table_id
    expected_rows = int(expected_rows)
    rows_found = -1

    try:
        # Wait for the table to be visible
        table_visible = WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, table_selector)
            )
        )
        print("table is vis: ", table_visible)
        # Check if tbody element exists
        tbody_tr_present = context.driver.find_elements(
            By.CSS_SELECTOR, f"{table_selector} tbody tr"
        )

        rows_found = len(context.driver.find_elements(By.CSS_SELECTOR, f"{table_selector} tbody tr"))

        assert int(rows_found) == expected_rows

    except TimeoutException:
        # Print additional information for debugging
        actual_rows = len(
            context.driver.find_elements(By.CSS_SELECTOR, f"{table_selector} tbody tr")
        )
        print(
            f"TimeoutException: Expected {expected_rows} rows, but found {actual_rows} rows."
        )
        raise


@when('I clear the item "{element_name}"')
def step_impl(context, element_name):
    """Clear the value of a field on the item form"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)

    # Clear the existing value
    element.clear()


@then(
    'I should not see "{text_string}" in the column "{column_index}" of the table "{table_id}"'
)
def step_impl(context, text_string, column_index, table_id):
    table_selector = "#" + table_id
    column_index = int(column_index)

    # Wait for the table to be present
    table_present = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, table_selector)
        )
    )

    # Wait for the absence of the value in the specified column
    value_absent = WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: all(
            text_string
            not in row.find_elements(
                By.CSS_SELECTOR, f"td:nth-child({column_index + 1})"
            )[0].text
            for row in driver.find_elements(
                By.CSS_SELECTOR, f"{table_selector} tbody tr"
            )
        )
    )

    assert value_absent

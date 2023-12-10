Feature: Wishlist Items Admin UI
    As a Wishlist Administrator
    I need a UI which interacts with a RESTful wishlist service
    So that I can keep track of all the items on a given wishlists

Scenario: Create Wishlist Item
    When I visit the "Admin UI Page"
    And I set the "Name" to "Jay's List"
    And I set the "Customer ID" to "9222"
    And I check the "Is Public" checkbox
    And I press the "Create" button
    Then I should see the message "Successfully created Wishlist"
    And The wishlist_id should match in both forms
    And The item "ID" field should be empty
    When I set the item "Product ID" to "987654"
    And I set the item "Product Name" to "Super Glue"
    And I set the item "Price" to "9.99"
    And I set the item "Quantity" to "11"
    And I press the item "Create" button
    Then I should see the message "Successfully added item"
    # And The item "ID" field should not be empty
    When I press the "Retrieve" button
    Then I should see "Jay's List" in the "Name" field
    And I should see "9222" in the "Customer ID" field
    And "Is Public" should "be" checked
    And The wishlist_id should match in both forms
    And The item "ID" field should be empty
    And The item "Product ID" field should be empty
    And The item "Product Name" field should be empty
    And The item "Price" field should be empty
    And The item "Quantity" field should be empty
    When I click the "Edit" button in the item table row "1"
    Then I should see "987654" in the item "Product ID" field
    And I should see "Super Glue" in the item "Product Name" field
    And I should see "9.99" in the item "Price" field
    And I should see "11" in the item "Quantity" field

Scenario: Delete Wishlist Item
    When I visit the "Admin UI Page"
    And I set the "Name" to "Jay's List"
    And I set the "Customer ID" to "9222"
    And I check the "Is Public" checkbox
    And I press the "Create" button
    Then I should see the message "Successfully created Wishlist"
    And The wishlist_id should match in both forms
    And The item "ID" field should be empty
    When I set the item "Product ID" to "987654"
    And I set the item "Product Name" to "Super Glue"
    And I set the item "Price" to "9.99"
    And I set the item "Quantity" to "11"
    And I press the item "Create" button
    Then I should see the message "Successfully added item"
    # And The item "ID" field should not be empty
    When I press the "Retrieve" button
    Then I should see "Jay's List" in the "Name" field
    And I should see "9222" in the "Customer ID" field
    And "Is Public" should "be" checked
    And The wishlist_id should match in both forms
    And The item "ID" field should be empty
    And The item "Product ID" field should be empty
    And The item "Product Name" field should be empty
    And The item "Price" field should be empty
    And The item "Quantity" field should be empty
    When I click the "Delete" button in the item table row "1"
    Then I should see the message "Successfully deleted item"
    And The item "ID" field should be empty
    And The item "Product ID" field should be empty
    And The item "Product Name" field should be empty
    And The item "Price" field should be empty
    And The item "Quantity" field should be empty
    And I should see "0" rows in the table "wishlist-items-table"
    # Adding 2 items
    When I set the item "Product ID" to "1234"
    And I set the item "Product Name" to "Super Glue"
    And I set the item "Price" to "9.99"
    And I set the item "Quantity" to "11"
    And I press the item "Create" button
    Then I should see the message "Successfully added item"
    When I clear the item "ID"
    When I set the item "Product ID" to "123456"
    And I set the item "Product Name" to "Super Glue"
    And I set the item "Price" to "9.99"
    And I set the item "Quantity" to "11"
    And I press the item "Create" button
    Then I should see the message "Successfully added item"
    When I press the "Retrieve" button
    Then I should see "Jay's List" in the "Name" field
    And I should see "9222" in the "Customer ID" field
    When I click the "Delete" button in the item table row "1"
    Then I should see the message "Successfully deleted item"
    And The item "ID" field should be empty
    And The item "Product ID" field should be empty
    And The item "Product Name" field should be empty
    And The item "Price" field should be empty
    And The item "Quantity" field should be empty
    And I should see "1" rows in the table "wishlist-items-table"
    When I click the "Edit" button in the item table row "1"
    Then I should see "123456" in the item "Product ID" field
    And I should see "Super Glue" in the item "Product Name" field
    And I should see "9.99" in the item "Price" field
    And I should see "11" in the item "Quantity" field

Scenario: Update Wishlist Item
    When I visit the "Admin UI Page"
    And I set the "Name" to "Jay's List"
    And I set the "Customer ID" to "9222"
    And I check the "Is Public" checkbox
    And I press the "Create" button
    Then I should see the message "Successfully created Wishlist"
    And The wishlist_id should match in both forms
    And The item "ID" field should be empty
    When I set the item "Product ID" to "987654"
    And I set the item "Product Name" to "Super Glue"
    And I set the item "Price" to "9.99"
    And I set the item "Quantity" to "11"
    And I press the item "Create" button
    Then I should see the message "Successfully added item"
    When I press the "Retrieve" button
    Then I should see "Jay's List" in the "Name" field
    And I should see "9222" in the "Customer ID" field
    And "Is Public" should "be" checked
    And The wishlist_id should match in both forms
    And The item "ID" field should be empty
    And The item "Product ID" field should be empty
    And The item "Product Name" field should be empty
    And The item "Price" field should be empty
    And The item "Quantity" field should be empty
    When I click the "Edit" button in the item table row "1"
    Then I should see "987654" in the item "Product ID" field
    And I should see "Super Glue" in the item "Product Name" field
    And I should see "9.99" in the item "Price" field
    And I should see "11" in the item "Quantity" field
    When I set the item "Quantity" to "15"
    And I press the item "Update" button
    Then I should see the message item "Successfully updated item"
    When I press the "Retrieve" button
    And I click the "Edit" button in the item table row "1"
    Then I should see "987654" in the item "Product ID" field
    And I should see "Super Glue" in the item "Product Name" field
    And I should see "9.99" in the item "Price" field
    And I should see "15" in the item "Quantity" field
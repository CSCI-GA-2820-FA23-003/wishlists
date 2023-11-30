Feature: Wishlists Admin UI
    As a Wishlist Administrator
    I need a UI which interacts with a RESTful wishlist service
    So that I can keep track of all customers wishlists

Scenario: The server is running
    When I visit the "Admin UI Page"
    Then I should see "Wishlist Admin UI" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Admin UI Page"
    And I set the "Name" to "Beckett's Halloween Costume List"
    And I set the "Customer ID" to "42"
    And I check the "Is Public" checkbox
    And I press the "Create" button
    Then I should see the message "Successfully created Wishlist"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Customer ID" field should be empty
    And "Is Public" should "not be" checked
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Beckett's Halloween Costume List" in the "Name" field
    And I should see "42" in the "Customer ID" field
    And "Is Public" should "be" checked

Scenario: Delete a Wishlist
    When I visit the "Admin UI Page"
    And I set the "ID" to "42"
    And I press the "Delete" button
    Then I should see the message "Successfully deleted Wishlist"
    When I press the "Retrieve" button
    Then I should see the message "Wishlist Could not be Found"

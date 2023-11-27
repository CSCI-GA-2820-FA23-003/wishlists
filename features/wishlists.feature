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
    And the "Is Public" field should be unchecked
    # When I paste the "Id" field
    # And I press the "Retrieve" button
    # Then I should see the message "Success"
    # And I should see "Happy" in the "Name" field
    # And I should see "Hippo" in the "Category" field
    # And I should see "False" in the "Available" dropdown
    # And I should see "Male" in the "Gender" dropdown
    # And I should see "2022-06-16" in the "Birthday" field

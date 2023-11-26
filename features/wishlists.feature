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

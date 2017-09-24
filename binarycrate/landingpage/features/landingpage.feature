Feature: Landing page behaviour

    Scenario: User is not logged in
        Given I access the url "/"
        Then the page source contains "Hello World"


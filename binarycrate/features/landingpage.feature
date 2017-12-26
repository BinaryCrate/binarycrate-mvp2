Feature: Cannot use the site if not logged in
  In order use binary crate I must log in
  As a web user
  If I browse to the home page I must be redirected to the login page

  Scenario: Browse to root page
    Given I browse to "http://webserver:8000/"
    When I wait for the browser to render the page
    Then I the browsers URL is "http://webserver:8000/accounts/login/?next=/"


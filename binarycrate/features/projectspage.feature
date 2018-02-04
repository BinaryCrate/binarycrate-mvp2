Feature: When logged on I can only see my projects
  In order use binary crate I must log in
  As a web user
  Once logged in I should be able to see my projects
  Once logged in I should not be able to see other users projects

  Scenario: Login and view the default project list
    Given I set up default credentials
    Given I set up default projects
    Given I browse to "/"
    When I wait for the browser to render the page
    When I login in with the default credentials
    Then I the browsers URL is "/"
    When I wait for the browser to render the page
    Then the browser window contains a project named "marksproject"
    Then the browser window does not contain a project named "hasibsproject"

  Scenario: Login and add a new project
    Given I set up default credentials
    Given I set up default projects
    Given I browse to "/"
    When I wait for the browser to render the page
    When I login in with the default credentials
    Then I the browsers URL is "/"
    When I wait for the browser to render the page
    Then the browser window does not contain a project named "Marks Second Project"
    Given I click on "a" with content "Create New"
    Then "div" with id "createNew" is visible
    Given I enter "Marks Second Project" in to the element with id "txtProjectName"
    When I click the "button" labelled "OK" inside the "div" with id "createNew"
    #When I wait for the browser to render the page
    #Then the database has a project named "Marks Second Project"
    Then the browser window contains a project named "Marks Second Project"
    



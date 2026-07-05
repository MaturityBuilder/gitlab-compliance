Feature: Jobs must inherit org security templates

  Scenario: Code-quality jobs must extend gitleaks template
    Given I have any job defined
    When its stage is code-quality
    Then it must contain extends
    And its extends must include ".gitleaks-template"

  Scenario: Deploy jobs must extend approved deploy template
    Given I have any job defined
    When its stage is deploy
    Then its extends must include ".approved-deploy-template"

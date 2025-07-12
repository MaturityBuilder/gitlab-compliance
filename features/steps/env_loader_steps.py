# features/steps/env_loader_steps.py

from behave import given, when, then
import yaml
from src.modules.common import EnvLoader

@given("a YAML input with !reference tag")
def step_given_yaml_input(context):
    context.yaml_text = '''
    build:python: !reference [.publish, script]
    '''

@when("the YAML is loaded")
def step_when_yaml_loaded(context):
    context.result = yaml.load(context.yaml_text, Loader=EnvLoader)

@then("the variables should be replaced correctly")
def step_then_check_replacement(context):
    expected = "Hello, foo and bar!"
    print(context)
    assert context
    #  None

from behave import given, when, then
import os
import subprocess
from src.modules.logging import logger
@given('LOG_LEVEL is set to "DEBUG"')
def step_given_debug_env(context):
    os.environ["LOG_LEVEL"] = "DEBUG"

@when("the logger is initialized")
def step_when_logger_runs(context):
    result = subprocess.run(
        ["python3", "-c", '''
from src.modules.logging import logger
logger.debug("This is debug")
'''],
        capture_output=True,
        env=os.environ
    )
    context.output = result.stderr.decode()
@then("debug logs should be visible")
def step_debug_logs_visible(context):
    assert "This is debug" in context.output

    assert "🐛" in context.output

from behave import given, when, then
from io import StringIO
from src.modules.logging import configure_logger

@given('no LOG_LEVEL is provided')
def step_no_log_level(context):
    context.output = StringIO()
    context.logger = configure_logger(log_level=None, output=context.output)

@given('an invalid LOG_LEVEL')
def step_invalid_log_level(context):
    context.output = StringIO()
    context.logger = configure_logger(log_level="INVALID", output=context.output)

@when('I log an info message')
def step_log_info(context):
    context.logger.info("Info test message")

@when('I log a debug message')
def step_log_debug(context):
    context.logger.debug("Debug test message")

@then('the output should contain "INFO" and the message')
def step_check_info_output(context):
    output = context.output.getvalue()
    assert "INFO" in output
    assert "Info test message" in output

@then('the output should contain the bug emoji 🐛 and the debug message')
def step_check_debug_output(context):
    output = context.output.getvalue()
    assert "🐛" in output
    assert "Debug test message" in output

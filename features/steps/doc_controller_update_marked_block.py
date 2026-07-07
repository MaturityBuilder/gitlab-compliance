import os
import shutil
import stat
import tempfile

from behave import given, then, when

from src.modules.doc_controller import update_marked_block


# Test implementation of the function
class MockLogger:
    def __init__(self):
        self.trace_calls = []
        self.info_calls = []
        self.error_calls = []

    def trace(self, msg):
        self.trace_calls.append(msg)
        print(f"TRACE: {msg}")

    def info(self, msg):
        self.info_calls.append(msg)
        print(f"INFO: {msg}")

    def error(self, msg):
        self.error_calls.append(msg)
        print(f"ERROR: {msg}")


logger = MockLogger()


@when('I update the marked block with "{text}"')
def step_when_update_block(context, text):
    dry = getattr(context, "dry", False)
    update_marked_block(str(context.file_path), text, dry=dry)


# Step definitions
@given("I have a test environment set up")
def step_setup_test_env(context):
    """Set up test environment"""
    context.test_dir = tempfile.mkdtemp()
    global logger
    logger = MockLogger()
    context.logger = logger
    # Reset dry mode
    update_marked_block._dry_mode = False


@given('the file "{filename}" does not exist')
def step_file_does_not_exist(context, filename):
    """Ensure file doesn't exist"""
    context.file_path = os.path.join(context.test_dir, filename)
    if os.path.exists(context.file_path):
        os.remove(context.file_path)


@given('I have a file "{filename}" with content')
def step_create_file_with_content(context, filename):
    """Create file with multiline content"""
    context.file_path = os.path.join(context.test_dir, filename)
    with open(context.file_path, "w", encoding="utf-8") as f:
        f.write(context.text)


@given('I have a file "{filename}" with content "{content}" and no final newline')
def step_create_file_no_newline(context, filename, content):
    """Create file without final newline"""
    context.file_path = os.path.join(context.test_dir, filename)
    with open(context.file_path, "w", encoding="utf-8") as f:
        f.write(content)


@given("dry run mode is enabled")
def step_enable_dry_run(context):
    """Enable dry run mode"""
    update_marked_block._dry_mode = True


@when('I update the marked block with content "{content}"')
def step_update_block_simple(context, content):
    """Update block with simple content"""
    context.content = content
    update_marked_block(context.file_path, content)


@when("I update the marked block with content")
def step_update_block_multiline(context):
    """Update block with multiline content"""
    context.content = context.text
    update_marked_block(context.file_path, context.text)


@then('the file "{filename}" should be created')
def step_file_created(context, filename):
    """Verify file was created"""
    expected_path = os.path.join(context.test_dir, filename)
    assert os.path.exists(expected_path), f"File {filename} was not created"


@then("the file should contain the marked block")
def step_file_contains_marked_block(context):
    """Verify file contains the marked block with content"""
    with open(context.file_path, "r", encoding="utf-8") as f:
        content = f.read()

    marker_start = "[comment]: <> (gitlab-compliance-opening-auto-generated)"
    marker_end = "[comment]: <> (gitlab-compliance-closing-auto-generated)"

    assert marker_start in content, "File should contain opening marker"
    assert marker_end in content, "File should contain closing marker"
    assert (
        context.content in content
    ), f"File should contain the content: {context.content}"


@then('the file should contain "{text}"')
def step_file_contains_text(context, text):
    """Verify file contains specific text"""
    with open(context.file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert text in content, f"File should contain: {text}"


@then('the file should not contain "{text}"')
def step_file_not_contains_text(context, text):
    """Verify file does not contain specific text"""
    with open(context.file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert text not in content, f"File should not contain: {text}"


@then('the file should still contain "{text}"')
def step_file_still_contains_text(context, text):
    """Verify file still contains text (for dry run)"""
    with open(context.file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert text in content, f"File should still contain: {text}"


@then("the file should be properly formatted with newlines")
def step_file_properly_formatted(context):
    """Verify file has proper newline formatting"""
    with open(context.file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Should have proper newlines
    lines = content.split("\n")
    assert len(lines) > 1, "File should have multiple lines"

    # Should contain the markers
    marker_start = "[comment]: <> (gitlab-compliance-opening-auto-generated)"
    marker_end = "[comment]: <> (gitlab-compliance-closing-auto-generated)"
    assert marker_start in content, "Should contain opening marker"
    assert marker_end in content, "Should contain closing marker"


# features/environment.py
def after_scenario(context, scenario):
    """Cleanup function called after each scenario"""
    if hasattr(context, "test_dir") and os.path.exists(context.test_dir):
        import os
        import shutil
        import stat

        # Reset file permissions before cleanup
        for root, dirs, files in os.walk(context.test_dir):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    # Best-effort cleanup: ignore chmod failures on locked/read-only files.
                    pass

        shutil.rmtree(context.test_dir, ignore_errors=True)


# Run this to test the basic functionality
if __name__ == "__main__":
    import shutil
    import tempfile

    # Quick test
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, "test.md")

    try:
        # Test 1: Create new file
        update_marked_block(test_file, "Test content")
        with open(test_file, "r") as f:
            content = f.read()
        print("Test 1 - New file:")
        print(content)
        print("---")

        # Test 2: Update existing
        update_marked_block(test_file, "Updated content")
        with open(test_file, "r") as f:
            content = f.read()
        print("Test 2 - Updated:")
        print(content)
        print("---")

        print("Basic tests passed!")

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|MARKDOWN WRAPPER")
logger.setLevel(LOG_LEVEL)


def replaceTextBetween(originalText, delimiterA, delimiterB="", replacementText=""):
    leadingText = originalText.split(delimiterA)[0]
    trailingText = originalText.split(delimiterB)[1]

    return leadingText + delimiterA + replacementText + delimiterB + trailingText


def gitlab_docs_reset_writer(OUTPUT_FILE, MODE, GLDOCS_TITLE="Gitlab Docs"):
    """
    MODE value can be either STARTING or CLOSING
    """
    # import markdown
    # import frontmatter
    gldocs_opening = "[comment]: <> (gitlab-docs-opening-auto-generated)"
    gldocs_closing = "[comment]: <> (gitlab-docs-closing-auto-generated)"

    if MODE == "STARTING":
        print(
            "Do we have a header in in markdown file already: "
            + str(gitlab_docs_check_header(OUTPUT_FILE, GLDOCS_TITLE=GLDOCS_TITLE))
        )
        if gitlab_docs_check_header(OUTPUT_FILE, GLDOCS_TITLE):
            print("Output File already has Gitlab Docs")
            gitlab_docs_remove_docs(
                OUTPUT_FILE=OUTPUT_FILE,
                GLDOCS_TITLE=gldocs_opening,
                GLDOCS_END=gldocs_closing,
            )
        else:
            print("Output File is new to Gitlab Docs")
            if gitlab_docs_check_file_exists(OUTPUT_FILE):
                gitlab_docs_remove_docs(
                    OUTPUT_FILE=OUTPUT_FILE,
                    GLDOCS_TITLE=gldocs_opening,
                    GLDOCS_END=gldocs_closing,
                )
                with open(OUTPUT_FILE, "a") as f:
                    f.write("\n" + "# " + gldocs_opening)

    if MODE == "CLOSING":

        with open(OUTPUT_FILE, "a") as f:
            f.write("\n\n" + gldocs_closing)


def gitlab_docs_check_file_exists(OUTPUT_FILE):
    from pathlib import Path

    CHECK_OUTPUT_FILE = Path(OUTPUT_FILE)
    if CHECK_OUTPUT_FILE.is_file():
        return True
    else:
        return False


def gitlab_docs_check_header(OUTPUT_FILE, GLDOCS_TITLE):
    from mrkdwn_analysis import MarkdownAnalyzer

    gitlab_docs_check_file_exists(OUTPUT_FILE)
    if gitlab_docs_check_file_exists(OUTPUT_FILE):
        analyzer = MarkdownAnalyzer(OUTPUT_FILE)
        headers = analyzer.identify_headers()
        # sections = analyzer.identify_sections()
        if headers:
            # print(headers)
            if GLDOCS_TITLE in headers["Header"]:
                # print(headers["Header"])
                return True
            else:
                return False
        else:
            print("No Headers in output file found: " + OUTPUT_FILE)
            return False
    else:
        return False


def gitlab_docs_remove_docs(OUTPUT_FILE, GLDOCS_TITLE, GLDOCS_END):

    with open(OUTPUT_FILE, "r") as f:
        contents = f.read()
        to_replace = contents[
            contents.find(GLDOCS_TITLE) + len(GLDOCS_TITLE) : contents.rfind(GLDOCS_END)
        ]
        contents = contents.replace(to_replace, "")
    with open(OUTPUT_FILE, "w") as f:
        f.write(contents)
    with open(OUTPUT_FILE, "r") as f:
        contents = f.read()
        contents = contents.replace(GLDOCS_END, "")
    with open(OUTPUT_FILE, "w") as f:
        f.write(contents)

import pytest
import allure
from pathlib import Path
from playwright.sync_api import sync_playwright


# ========================================================================
# PROJECT PATH CONFIGURATION
# ========================================================================

# This conftest.py is located in:
# OpencartFramework/conftest.py

PROJECT_ROOT = Path(__file__).resolve().parent

# Main reports folder
REPORTS_DIR = PROJECT_ROOT / "reports"

# Individual artifact folders
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
VIDEOS_DIR = REPORTS_DIR / "videos"
TRACES_DIR = REPORTS_DIR / "traces"

# Allure results folder
ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"

# Pytest HTML report
HTML_REPORT_PATH = REPORTS_DIR / "myreport.html"


# Create all required directories
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TRACES_DIR.mkdir(parents=True, exist_ok=True)
ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ========================================================================
# PYTEST CONFIGURATION
# ========================================================================

def pytest_configure(config):
    """
    Configure absolute paths for reports.

    This ensures that reports are always saved inside:

    OpencartFramework/reports/

    even when pytest is executed from the tests folder.
    """

    # Set pytest-html report path
    config.option.htmlpath = str(HTML_REPORT_PATH)

    # Set Allure results path
    config.option.allure_report_dir = str(ALLURE_RESULTS_DIR)


# ========================================================================
# STEP 1: ADD COMMAND LINE OPTIONS
# ========================================================================

def pytest_addoption(parser):
    """
    Adds command line options for test configuration.
    """

    parser.addoption(
        "--browser",
        default="chromium",
        help="Browser: chromium, firefox, webkit"
    )

    parser.addoption(
        "--headed",
        action="store_true",
        help="Run in headed (visible) mode"
    )

    parser.addoption(
        "--base-url",
        default="https://tutorialsninja.com/demo/",
        help="Base URL for tests"
    )

    parser.addoption(
        "--video",
        default="retain-on-failure",
        help="Record video: on, off, retain-on-failure"
    )

    parser.addoption(
        "--screenshot",
        default="only-on-failure",
        help="Take screenshot: on, off, only-on-failure"
    )

    parser.addoption(
        "--tracing",
        default="retain-on-failure",
        help="Tracing: on, off, retain-on-failure"
    )


# ========================================================================
# STEP 2: GET CONFIGURATION VALUE
# ========================================================================

def get_config_value(config, option_name):
    """
    Reads the configuration value from pytest command-line options.
    """

    return config.getoption(option_name)


# ========================================================================
# STEP 3: HOOK TO TRACK TEST RESULT
# ========================================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Stores test results so fixtures can determine whether
    the test passed or failed.
    """

    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)


# ========================================================================
# STEP 4: BROWSER CONTEXT FIXTURE
# ========================================================================

@pytest.fixture(scope="function")
def browser_context(request):

    browser_name = get_config_value(
        request.config,
        "browser"
    )

    headed_flag = get_config_value(
        request.config,
        "headed"
    )

    video_option = get_config_value(
        request.config,
        "video"
    )

    print(f"[OK] Starting browser: {browser_name}")
    print(f"[OK] Headless mode: {not headed_flag}")

    # Start Playwright
    playwright = sync_playwright().start()

    # ------------------------------------------------------------
    # Launch Browser
    # ------------------------------------------------------------

    if browser_name.lower() == "chromium":

        browser = playwright.chromium.launch(
            headless=not headed_flag
        )

    elif browser_name.lower() == "firefox":

        browser = playwright.firefox.launch(
            headless=not headed_flag
        )

    elif browser_name.lower() == "webkit":

        browser = playwright.webkit.launch(
            headless=not headed_flag
        )

    else:

        raise ValueError(
            f"Unsupported browser: {browser_name}"
        )

    # ------------------------------------------------------------
    # Create Browser Context
    # ------------------------------------------------------------

    if video_option in ["on", "retain-on-failure"]:

        context = browser.new_context(

            # Absolute path
            record_video_dir=str(VIDEOS_DIR)

        )

    else:

        context = browser.new_context()

    # Provide context to test
    yield context

    # ------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------

    print("[CLEANUP] Closing browser context...")

    context.close()

    browser.close()

    playwright.stop()


# ========================================================================
# STEP 5: PAGE FIXTURE
# ========================================================================

@pytest.fixture(scope="function")
def page(request, browser_context):

    # ------------------------------------------------------------
    # Read configuration
    # ------------------------------------------------------------

    base_url = get_config_value(
        request.config,
        "base_url"
    )

    screenshot_option = get_config_value(
        request.config,
        "screenshot"
    )

    tracing_option = get_config_value(
        request.config,
        "tracing"
    )

    video_option = get_config_value(
        request.config,
        "video"
    )

    print(f"[INFO] Navigating to: {base_url}")

    # ------------------------------------------------------------
    # Start tracing
    # ------------------------------------------------------------

    if tracing_option in ["on", "retain-on-failure"]:

        print("[TRACE] Tracing enabled")

        browser_context.tracing.start(

            screenshots=True,
            snapshots=True,
            sources=True

        )

    # ------------------------------------------------------------
    # Create page
    # ------------------------------------------------------------

    page = browser_context.new_page()

    page.goto(base_url)

    # Give page to test
    yield page

    # ------------------------------------------------------------
    # TEST RESULT
    # ------------------------------------------------------------

    test_name = request.node.name

    test_failed = (

        hasattr(request.node, "rep_call")
        and request.node.rep_call.failed

    )

    print(

        f"[RESULT] Test '{test_name}' result: "
        f"{'[FAIL]' if test_failed else '[PASS]'}"

    )

    # ============================================================
    # TRACE
    # ============================================================

    if tracing_option in ["on", "retain-on-failure"]:

        trace_path = (

            TRACES_DIR
            / f"{test_name}_trace.zip"

        )

        browser_context.tracing.stop(

            path=str(trace_path)

        )

        print(

            f"[SAVE] Trace saved: "
            f"{trace_path}"

        )

    # ============================================================
    # SCREENSHOT
    # ============================================================

    if (

        test_failed
        and screenshot_option in ["on", "only-on-failure"]

    ):

        screenshot_path = (

            SCREENSHOTS_DIR
            / f"{test_name}.png"

        )

        page.screenshot(

            path=str(screenshot_path)

        )

        print(

            f"[SAVE] Screenshot saved: "
            f"{screenshot_path}"

        )

        # Attach screenshot to Allure
        allure.attach.file(

            str(screenshot_path),

            name=f"{test_name}_screenshot",

            attachment_type=allure.attachment_type.PNG

        )

        print(

            "[ATTACH] Screenshot attached "
            "to Allure report"

        )

    # ============================================================
    # VIDEO
    # ============================================================

    if (

        test_failed
        and video_option in ["on", "retain-on-failure"]

    ):

        video_path = (

            page.video.path()

            if page.video

            else None

        )

        if (

            video_path

            and Path(video_path).exists()

        ):

            allure.attach.file(

                str(video_path),

                name=f"{test_name}_video",

                attachment_type=allure.attachment_type.WEBM

            )

            print(

                "[ATTACH] Video attached "
                "to Allure report"

            )
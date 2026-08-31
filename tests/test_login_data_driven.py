```python
import time
import pytest
from pathlib import Path
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.my_account_page import MyAccountPage

from Utilities.data_reader_util import read_json_data


# ---------------------------------------------------------
# Get project root directory
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# JSON file path
# ---------------------------------------------------------
JSON_FILE = PROJECT_ROOT / "testdata" / "logindata.json"


# ---------------------------------------------------------
# Read test data from JSON
# ---------------------------------------------------------
json_data = read_json_data(str(JSON_FILE))


# ---------------------------------------------------------
# Data Driven Test
# ---------------------------------------------------------
@pytest.mark.datadriven
@pytest.mark.sanity
@pytest.mark.parametrize(
    "testName,email,password,expected",
    json_data
)
def test_login_data_driven(
        page,
        testName,
        email,
        password,
        expected
):

    """
    Verify login functionality using multiple sets of
    login credentials from JSON file.
    """

    # -----------------------------------------------------
    # Page Object Initialization
    # -----------------------------------------------------
    home_page = HomePage(page)
    login_page = LoginPage(page)
    my_account_page = MyAccountPage(page)

    # -----------------------------------------------------
    # Step 1: Navigate to Login Page
    # -----------------------------------------------------
    home_page.click_my_account()
    home_page.click_login()

    # -----------------------------------------------------
    # Step 2: Login using JSON data
    # -----------------------------------------------------
    login_page.login(email, password)

    # -----------------------------------------------------
    # Step 3: Wait for response
    # -----------------------------------------------------
    time.sleep(3)

    # -----------------------------------------------------
    # Step 4: Verify result
    # -----------------------------------------------------
    if expected.lower() == "success":

        expect(
            my_account_page.get_my_account_page_heading()
        ).to_be_visible(timeout=3000)

    else:

        expect(
            login_page.get_login_error()
        ).to_be_visible(timeout=3000)
```

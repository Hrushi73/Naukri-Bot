from playwright.sync_api import sync_playwright

def test_naukri_login_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.naukri.com/nlogin/login?URL=https://www.naukri.com/mnjuser/homepage")
        assert "Login" in page.title()
        page.fill('input[id="usernameField"]', 'hrushikeshmalshikare710@gmail.com')
        page.fill('input[id="passwordField"]', 'Hrushi710@naukri')
        page.click('button[type="submit"]')
        page.wait_for_load_state('load')

        # there is job button which show options, select recommended jobs
        # page.click('div:has-text("Jobs")')
        # page.click('div:has-text("Recommended Jobs")')
        page.get_by_role("link", name="Jobs").click()
        page.get_by_role("link", name="Recommended Jobs").click()


        # page.wait_for_timeout(60000)  # wait for 1 minute
        browser.close()
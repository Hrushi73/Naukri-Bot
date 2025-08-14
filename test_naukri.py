from playwright.sync_api import sync_playwright

def test_naukri_apply_recommended_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.naukri.com/nlogin/login?URL=https://www.naukri.com/mnjuser/homepage")
        assert "Login" in page.title()
        page.fill('input[id="usernameField"]', 'hrushikeshmalshikare710@gmail.com')
        page.fill('input[id="passwordField"]', 'Hrushi710@naukri')
        page.click('button[type="submit"]')
        page.wait_for_load_state('load')

        # Navigate to Recommended Jobs
        page.click('nav >> text=Jobs')
        # page.click('nav >> text=Recommended Jobs')
        page.wait_for_url("**/mnjuser/recommendedjobs")

        # Wait for job cards to load
        page.wait_for_selector('article.jobTuple')

        # Select up to 5 job checkboxes
        checkboxes = page.query_selector_all('article.jobTuple input[type="checkbox"]')
        for checkbox in checkboxes[:5]:
            checkbox.check()
            page.wait_for_timeout(500)  # slight delay for UI update

        # Click the Apply button
        page.click('button:has-text("Apply")')
        page.wait_for_timeout(2000)  # wait for any confirmation

        browser.close()


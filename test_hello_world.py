from playwright.sync_api import sync_playwright

def test_hello_world():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://naukri.com')
        browser.close()

# test_hello_world()
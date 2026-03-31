import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

URL = os.getenv("MAPLEWOOD_URL")
USERNAME = os.getenv("MAPLEWOOD_USER")
PASSWORD = os.getenv("MAPLEWOOD_PASS")

def scrape_grades():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)
        page.fill("#txtUsername", USERNAME)
        page.fill("#txtPassword", PASSWORD)
        page.click("#btnLogin")
        page.wait_for_load_state("networkidle")
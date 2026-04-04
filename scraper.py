import os
import time
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
        page.fill("#username", USERNAME)
        page.click("[name='cmdLogin']")
        page.wait_for_selector("#pwd")
        page.fill("#pwd", PASSWORD)
        page.click("[name='cmdLogin']")
        time.sleep(8)

        print("Clicking Mar 20 link...")
        page.evaluate("""() => {
            let bottom = document.getElementsByName('bottom')[0];
            let bottomRight = bottom.contentDocument.getElementsByName('bottomRight')[0];
            let anchors = bottomRight.contentDocument.getElementsByTagName('a');
            for(let a of anchors) {
                if(a.innerText.trim() === 'Mar 20') {
                    a.click();
                    return 'clicked!';
                }
            }
        }""")

        time.sleep(5)

        print("Reading markbook...")
        content = page.evaluate("""() => {
            let bottom = document.getElementsByName('bottom')[0];
            let bottomRight = bottom.contentDocument.getElementsByName('bottomRight')[0];
            let doc = bottomRight.contentDocument;
            let rows = doc.querySelectorAll('table tr');
            let results = [];
            for(let row of rows) {
                let cells = row.querySelectorAll('td');
                if(cells.length === 5) {
                    let rowData = [];
                    for(let cell of cells) {
                        rowData.push(cell.innerText.trim());
                    }
                    results.push(rowData);
                }
            }
            return results;
        }""")
        
        print("\nMathematics Grades:")
        print(f"{'Item':<45} {'Mark':<8} {'Date':<15} {'Weight':<8} {'Out of'}")
        print("-" * 90)
        for row in content:
            print(f"{row[0]:<45} {row[1]:<8} {row[2]:<15} {row[3]:<8} {row[4]}")

        page.pause()

scrape_grades()
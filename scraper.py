import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

URL = os.getenv("MAPLEWOOD_URL")
USERNAME = os.getenv("MAPLEWOOD_USER")
PASSWORD = os.getenv("MAPLEWOOD_PASS")

CLASSES = [
    {"name": "Mathematics", "date": "Mar 20"},
    {"name": "Anthropology, Psychology & Sociology", "date": "Apr 01"},
    {"name": "Hospitality and Tourism Technology", "date": "Mar 26"},
    {"name": "Geographie", "date": "Apr 02"},
]

def click_and_scrape(page, class_name, date_text):
    print(f"\nClicking {class_name} ({date_text})...")
    page.evaluate(f"""() => {{
        let bottom = document.getElementsByName('bottom')[0];
        let bottomRight = bottom.contentDocument.getElementsByName('bottomRight')[0];
        let anchors = bottomRight.contentDocument.getElementsByTagName('a');
        for(let a of anchors) {{
            if(a.innerText.trim() === '{date_text}') {{
                a.click();
                return 'clicked!';
            }}
        }}
    }}""")

    time.sleep(5)

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

    print(f"\n{class_name} Grades:")
    print(f"{'Item':<45} {'Mark':<8} {'Date':<15} {'Weight':<8} {'Out of'}")
    print("-" * 90)
    for row in content:
        if row[0] != "Categories / Item":
            print(f"{row[0]:<45} {row[1]:<8} {row[2]:<15} {row[3]:<8} {row[4]}")

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

        for cls in CLASSES:
            click_and_scrape(page, cls["name"], cls["date"])

        page.pause()

scrape_grades()
import os
import time
import json
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
    print(f"\nScraping {class_name}...")
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

    grades = []
    for row in content:
        if row[0] == "Categories / Item":
            continue
        grades.append({
            "item": row[0],
            "mark": row[1],
            "date": row[2],
            "weight": row[3],
            "out_of": row[4]
        })

    return grades

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

        all_grades = {}

        for cls in CLASSES:
            grades = click_and_scrape(page, cls["name"], cls["date"])
            all_grades[cls["name"]] = grades
            print(f"Saved {len(grades)} rows for {cls['name']}")

        with open("grades.json", "w") as f:
            json.dump(all_grades, f, indent=2)

        print("\nGrades saved to grades.json!")
        browser.close()

scrape_grades()
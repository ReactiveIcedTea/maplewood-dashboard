import os
import time
import json
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

URL = os.getenv("MAPLEWOOD_URL")
USERNAME = os.getenv("MAPLEWOOD_USER")
PASSWORD = os.getenv("MAPLEWOOD_PASS")

def get_class_list(page):
    print("Reading class list...")
    rows = page.evaluate("""() => {
        let bottom = document.getElementsByName('bottom')[0];
        let bottomRight = bottom.contentDocument.getElementsByName('bottomRight')[0];
        let doc = bottomRight.contentDocument;
        let rows = doc.querySelectorAll('table tr');
        let results = [];
        for(let row of rows) {
            let cells = row.querySelectorAll('td');
            if(cells.length === 2) {
                let name = cells[0].innerText.trim();
                let date = cells[1].innerText.trim();
                if(name && date && name !== 'Class') {
                    results.push({name: name, date: date});
                }
            }
        }
        return results;
    }""")
    return rows

def click_and_scrape(page, class_name, date_text):
    print(f"\nScraping {class_name} ({date_text})...")
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

def generate_html(grades):
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Maplewood Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
        h2 {
            color: #2980b9;
            border-bottom: 2px solid #2980b9;
            padding-bottom: 5px;
            margin-top: 40px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th {
            background-color: #2980b9;
            color: white;
            padding: 10px;
            text-align: left;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f0f7ff;
        }
        .term-row {
            background-color: #eaf4ff;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>📚 Maplewood Grade Dashboard</h1>
"""

    for class_name, rows in grades.items():
        html += f"<h2>{class_name}</h2>\n"
        html += """<table>
            <tr>
                <th>Item</th>
                <th>Mark</th>
                <th>Date</th>
                <th>Weight</th>
                <th>Out of</th>
            </tr>\n"""
        for row in rows:
            row_class = 'term-row' if row['item'].lower().startswith('term') else ''
            html += f"""            <tr class="{row_class}">
                <td>{row['item']}</td>
                <td>{row['mark']}</td>
                <td>{row['date']}</td>
                <td>{row['weight']}</td>
                <td>{row['out_of']}</td>
            </tr>\n"""
        html += "</table>\n"

    html += "</body>\n</html>"

    with open("index.html", "w") as f:
        f.write(html)
    print("Dashboard generated as index.html!")

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

        classes = get_class_list(page)
        print(f"Found {len(classes)} classes:")
        for cls in classes:
            print(f"  {cls['name']} → {cls['date']}")

        all_grades = {}
        for cls in classes:
            grades = click_and_scrape(page, cls["name"], cls["date"])
            all_grades[cls["name"]] = grades
            print(f"Saved {len(grades)} rows for {cls['name']}")

        with open("grades.json", "w") as f:
            json.dump(all_grades, f, indent=2)

        print("\nGrades saved to grades.json!")
        generate_html(all_grades)
        browser.close()
        os.system("cp index.html /mnt/c/Users/rando/index.html")
        os.system('powershell.exe Start-Process "C:\\Users\\rando\\index.html"')
        print("Dashboard opened in browser!")

scrape_grades()
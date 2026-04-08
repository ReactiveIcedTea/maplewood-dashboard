import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    with open("grades.json", "r") as f:
        grades = json.load(f)
    return render_template("index.html", grades=grades)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
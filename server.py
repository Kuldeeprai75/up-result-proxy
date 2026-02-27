from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def home():
    return "Result Proxy Running"

@app.route("/api/result")
def result():

    roll = request.args.get("roll")
    if not roll:
        return jsonify({"status":"error","message":"Roll required"})

    url = f"https://www.amarujala.com/results/up-board/upmsp-up-board-10th-result-2025?roll={roll}"

    headers = {"User-Agent":"Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    data = {}
    subjects = []

    info = soup.find_all("div", class_="col-md-6")
    for i in info:
        text = i.get_text(strip=True)
        if ":" in text:
            key,value = text.split(":",1)
            data[key.strip()] = value.strip()

    table = soup.find("table")
    if table:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                subjects.append({
                    "subject": cols[0].text.strip(),
                    "theory": cols[1].text.strip(),
                    "practical": cols[2].text.strip(),
                    "total": cols[3].text.strip()
                })

    return jsonify({
        "status":"success",
        "info":data,
        "subjects":subjects
    })

if __name__ == "__main__":
    app.run()

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def home():
    return "UP Result Proxy Running ✅"

@app.route("/api/result")
def result():

    roll = request.args.get("roll")
    if not roll:
        return jsonify({"status":"error","message":"Roll required"})

    url = f"https://www.amarujala.com/results/up-board/upmsp-up-board-10th-result-2025?roll={roll}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {}
    subjects = []

    # Extract Roll & Name
    info_rows = soup.find_all("div", class_="col-md-6")
    for row in info_rows:
        text = row.get_text(strip=True)
        if ":" in text:
            key, value = text.split(":",1)
            data[key.strip()] = value.strip()

    # Extract Marks Table
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")[2:]  # skip header rows

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                subjects.append({
                    "subject": cols[0].text.strip(),
                    "marks": cols[1].text.strip(),
                    "practical": cols[2].text.strip(),
                    "total": cols[3].text.strip(),
                    "grade": cols[4].text.strip()
                })

    # Extract Result Status
    result_status = soup.find(text=lambda x: "PASSED" in str(x) or "FAILED" in str(x))
    if result_status:
        data["Result"] = result_status.strip()

    if not data:
        return jsonify({"status":"error","message":"Result not found"})

    return jsonify({
        "status":"success",
        "info":data,
        "subjects":subjects
    })

if __name__ == "__main__":
    app.run()

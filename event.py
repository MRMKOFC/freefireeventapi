from flask import Flask, request, jsonify, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

ALLOWED_REGIONS = ["ID", "IND", "NA", "PK", "BR", "ME", "SG", "BD", "TW", "TH", "VN", "CIS", "EU", "SAC", "IND-HN"]

@app.route('/')
def index():
    return "Welcome to the events API. Use /events to get events."

@app.route('/events', methods=['GET'])
def get_events():
    region = request.args.get('region', 'IND').upper()

    if region not in ALLOWED_REGIONS:
        return jsonify({"error": f"Invalid region. Allowed regions: {', '.join(ALLOWED_REGIONS)}"}), 400

    url = f"https://freefireleaks.vercel.app/events"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error if request fails
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch data", "details": str(e)}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('div', class_='poster')

    events = []
    current_time = int(datetime.now().timestamp())

    for element in elements:
        data_start = element.get('data-start')
        data_end = element.get('data-end')

        if not data_start or not data_end:
            continue  # Skip missing elements

        data_start = int(data_start)
        data_end = int(data_end)
        desc = element.get('desc', '')

        start_formatted = datetime.utcfromtimestamp(data_start).strftime('%Y-%m-%d %H:%M:%S')
        end_formatted = datetime.utcfromtimestamp(data_end).strftime('%Y-%m-%d %H:%M:%S')

        status = "Upcoming" if current_time < data_start else "Active" if current_time <= data_end else "Expired"

        img_tag = element.find('img')
        src = img_tag['src'] if img_tag else ''

        title_tag = element.find('p')
        poster_title = title_tag.get_text().strip() if title_tag else ''

        events.append({
            "poster-title": poster_title,
            "start": start_formatted,
            "end": end_formatted,
            "desc": desc,
            "src": src,
            "status": status
        })

    response_data = {
        "credit": "@MK",
        "region": region,
        "events": events
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)

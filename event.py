from flask import Flask, request, jsonify, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

app = Flask(__name__)

ALLOWED_REGIONS = ["ID", "IND", "NA", "PK", "BR", "ME", "SG", "BD", "TW", "TH", "VN", "CIS", "EU", "SAC", "IND-HN"]

@app.route('/')
def index():
    return "Welcome to the events API. Use /events to get events."

@app.route('/events', methods=['GET'])
def get_events():
    region = request.args.get('region', 'IND').upper()

    if region not in ALLOWED_REGIONS:
        return jsonify({
            "error": f"Invalid region. Allowed regions: {', '.join(ALLOWED_REGIONS)}"
        }), 400

    url = f"https://freefireleaks.vercel.app/events/{region}"

    response = requests.get(url, verify=False)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    elements = soup.find_all('div', class_='poster')

    events = []
    current_time = int(datetime.now().timestamp())

    for element in elements:
        data_start = int(element.get('data-start'))
        data_end = int(element.get('data-end'))
        desc = element.get('desc')

        start_formatted = datetime.utcfromtimestamp(data_start).strftime('%Y-%m-%d %H:%M:%S')
        end_formatted = datetime.utcfromtimestamp(data_end).strftime('%Y-%m-%d %H:%M:%S')

        if current_time < data_start:
            status = "Upcoming"
        elif current_time >= data_start and current_time <= data_end:
            status = "Active"
        else:
            status = "Expired"

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
        "credit": "@PikaApis",
        "region": region,
        "events": events
    }

    response_json = json.dumps(response_data, ensure_ascii=False, indent=4, separators=(',', ': '))

    return Response(response_json, content_type='application/json; charset=utf-8')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_URL = "https://xv.ct.ws/event/"

def fetch_regions():
    """Scrape the base event page to get available region codes dynamically."""
    try:
        response = requests.get(BASE_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Buttons contain region codes
    buttons = soup.find_all("button")
    regions = [btn.get_text(strip=True).upper() for btn in buttons if btn.get_text(strip=True)]
    return regions

@app.route('/')
def index():
    return "Welcome to the events API. Use /events to get events or /regions to list available regions."

@app.route('/regions', methods=['GET'])
def get_regions():
    regions = fetch_regions()
    if not regions:
        return jsonify({"error": "Failed to fetch regions"}), 500
    return jsonify({"regions": regions})

@app.route('/events', methods=['GET'])
def get_events():
    region = request.args.get('region', 'IND').upper()

    # Fetch dynamic regions
    regions = fetch_regions()
    if not regions:
        return jsonify({"error": "Failed to fetch regions"}), 500

    if region not in regions:
        return jsonify({"error": f"Invalid region. Allowed regions: {', '.join(regions)}"}), 400

    # Region-specific page
    url = f"{BASE_URL}?region={region}"

    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })
        response.raise_for_status()
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
            continue

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

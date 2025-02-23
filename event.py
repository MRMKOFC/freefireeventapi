from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)  # Enable CORS

ALLOWED_REGIONS = ["ID", "IND", "NA", "PK", "BR", "ME", "SG", "BD", "TW", "TH", "VN", "CIS", "EU", "SAC", "IND-HN"]

# Cache to store API responses (reduces repeated requests)
CACHE = {}
CACHE_EXPIRY = timedelta(minutes=10)  # Cache data for 10 minutes

def fetch_events(region):
    url = f"https://freefireleaks.vercel.app/events/{region}"

    try:
        response = requests.get(url, timeout=5, verify=False)  # Set timeout to 5 seconds
        response.raise_for_status()  # Raise error if request fails
    except requests.RequestException as e:
        return {"error": f"Failed to fetch events: {str(e)}"}, 500

    soup = BeautifulSoup(response.text, 'lxml')  # Faster parsing with lxml
    elements = soup.find_all('div', class_='poster')

    events = []
    current_time = int(datetime.now().timestamp())

    for element in elements:
        try:
            data_start = int(element.get('data-start', 0))
            data_end = int(element.get('data-end', 0))
            desc = element.get('desc', '')

            start_formatted = datetime.utcfromtimestamp(data_start).strftime('%Y-%m-%d %H:%M:%S')
            end_formatted = datetime.utcfromtimestamp(data_end).strftime('%Y-%m-%d %H:%M:%S')

            status = "Upcoming" if current_time < data_start else "Active" if current_time <= data_end else "Expired"

            img_tag = element.find('img')
            src = img_tag['src'] if img_tag else ''

            title_tag = element.find('p')
            poster_title = title_tag.get_text(strip=True) if title_tag else ''

            events.append({
                "poster-title": poster_title,
                "start": start_formatted,
                "end": end_formatted,
                "desc": desc,
                "src": src,
                "status": status
            })
        except Exception as e:
            print(f"Error parsing event: {e}")

    return {
        "credit": "MK",
        "region": region,
        "events": events
    }

@app.route('/')
def index():
    return "Welcome to the optimized Free Fire events API. Use /events?region=IND to get events."

@app.route('/events', methods=['GET'])
def get_events():
    region = request.args.get('region', 'IND').upper()

    if region not in ALLOWED_REGIONS:
        return jsonify({"error": f"Invalid region. Allowed regions: {', '.join(ALLOWED_REGIONS)}"}), 400

    # Check if cached data is available
    if region in CACHE and datetime.now() - CACHE[region]["time"] < CACHE_EXPIRY:
        return jsonify(CACHE[region]["data"])

    # Fetch new data
    response_data = fetch_events(region)
    
    if isinstance(response_data, tuple):  # If fetch_events returned an error
        return jsonify(response_data[0]), response_data[1]

    # Store in cache
    CACHE[region] = {"data": response_data, "time": datetime.now()}

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
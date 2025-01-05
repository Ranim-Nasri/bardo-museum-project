from flask import Blueprint, jsonify
import requests

google_bp = Blueprint('google', __name__)

API_KEY = 'AIzaSyBVezeNR4Dn_K1ETIrnBJnDy9iyIKVc-bE'
CX = '642ef41d594bc4032'

def fetch_google_data(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Google API response:", data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Google: {e}")
        return None

@google_bp.route('/fetch-google-info/<category_name>', methods=['GET'])  # Modified this line
def fetch_google_info(category_name):  # Now the parameter is properly received
    search_query = f"{category_name} Bardo Museum"
    google_data = fetch_google_data(search_query)
    
    if google_data and 'items' in google_data:
        print(f"Searching for: {search_query}")
        results = google_data['items']
        return jsonify(results), 200
    else:
        return jsonify({"error": "No information found."}), 404
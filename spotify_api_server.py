
from flask import Flask, request, jsonify
import requests
import base64
import os

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = Flask(__name__)

def get_access_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64_auth_str}"},
        data={"grant_type": "client_credentials"}
    )

    if response.status_code != 200:
        return None

    return response.json()["access_token"]

@app.route("/spotify-link", methods=["POST"])
def spotify_link():
    data = request.get_json()
    query = data.get("query")
    access_token = get_access_token()

    if not access_token:
        return jsonify({"error": "Token Error"}), 500

    search_response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": "track", "limit": 1}
    )

    if search_response.status_code != 200:
        return jsonify({"error": "Search Error"}), 500

    results = search_response.json()
    items = results.get("tracks", {}).get("items", [])

    if not items:
        return jsonify({"error": "No track found"}), 404

    track = items[0]
    return jsonify({
        "url": track["external_urls"]["spotify"]
    })

if __name__ == "__main__":
    app.run(debug=True)

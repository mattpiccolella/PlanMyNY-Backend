from flask import Flask, jsonify
import requests

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyDhoZ2Yyii_wvZaWSqUu4BilsVAfJHZIzk"
GOOGLE_PLACES_BASE_STRING = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
GOOGLE_DETAILS_BASE_STRING = "https://maps.googleapis.com/maps/api/place/details/json?reference="
GOOGLE_MAPS_BASE_STRING = "http://maps.googleapis.com/maps/api/staticmap?"

COLUMBIA_LAT = "40.807001"
COLUMBIA_LONG = "-73.9640299"

@app.route("/")
def hello():
    url = GOOGLE_PLACES_BASE_STRING + COLUMBIA_LAT + "," + COLUMBIA_LONG + "&radius=10000&types=museum&sensor=false&key=" + GOOGLE_API_KEY
    response_dict = requests.get(url).json()
    return jsonify(response_dict)

if __name__ == "__main__":
    app.run()

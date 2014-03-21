from flask import Flask, jsonify
import requests, random

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyDhoZ2Yyii_wvZaWSqUu4BilsVAfJHZIzk"
GOOGLE_PLACES_BASE_STRING = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
GOOGLE_DETAILS_BASE_STRING = "https://maps.googleapis.com/maps/api/place/details/json?reference="
GOOGLE_MAPS_BASE_STRING = "http://maps.googleapis.com/maps/api/staticmap?"
GOOGLE_ITEMS = "amusement_park|art_gallery|library|museum|night_club|park|shopping_mall|zoo|stadium|movie_theater"
GOOGLE_PHOTO = "https://maps.googleapis.com/maps/api/place/photo?photo_reference="

COLUMBIA_LAT = "40.807001"
COLUMBIA_LONG = "-73.9640299"

@app.route("/")
def hello():
    url = GOOGLE_PLACES_BASE_STRING + COLUMBIA_LAT + "," + COLUMBIA_LONG + "&radius=10000&types=" + GOOGLE_ITEMS + "&sensor=false&key=" + GOOGLE_API_KEY
    response_dict = requests.get(url).json()
    random_index = random.randint(0,len(response_dict['results']) - 1)
    random_item = response_dict['results'][random_index]
    c = {}
    c['lat'] = random_item['geometry']['location']['lat']
    c['long'] = random_item['geometry']['location']['lng']
    c['icon'] = random_item['icon']
    c['name'] = random_item['name']
    c['address'] = random_item['vicinity']
    if 'photos' in random_item:
        photo_ref = random_item['photos'][0]['photo_reference']
        photo_link = GOOGLE_PHOTO + photo_ref + "&senser=false&key=" + GOOGLE_API_KEY + "&maxheight=300"
    else:
        photo_link = "N/A"
    c['photo'] = photo_link
    return jsonify(c)

if __name__ == "__main__":
    app.debug = True
    app.run()

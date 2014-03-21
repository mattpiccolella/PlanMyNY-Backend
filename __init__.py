from flask import Flask, jsonify
import requests, random, html2text

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyDhoZ2Yyii_wvZaWSqUu4BilsVAfJHZIzk"
GOOGLE_PLACES_BASE_STRING = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
GOOGLE_DETAILS_BASE_STRING = "https://maps.googleapis.com/maps/api/place/details/json?reference="
GOOGLE_MAPS_BASE_STRING = "http://maps.googleapis.com/maps/api/staticmap?"
GOOGLE_ITEMS = "amusement_park|art_gallery|library|museum|night_club|park|shopping_mall|zoo|stadium|movie_theater"
GOOGLE_PHOTO = "https://maps.googleapis.com/maps/api/place/photo?photo_reference="

COLUMBIA_LAT = "40.807001"
COLUMBIA_LONG = "-73.9640299"

NY_TIMES_API_KEY = "ac8e622d58c2753ea21809d358c146cb:9:68789349"
NEW_YORK_TIMES_BASE_STRING = "http://api.nytimes.com/svc/events/v2/listings.json?api-key=" + NY_TIMES_API_KEY

@app.route("/")
def hello():
    c = {}
    location = random_location()
    event = random_event(location['lat'], location['long'])
    c['location'] = location
    c['event'] = event
    return jsonify(c)

def random_location():
    url = GOOGLE_PLACES_BASE_STRING + COLUMBIA_LAT + "," + COLUMBIA_LONG + "&radius=10000&types=" + GOOGLE_ITEMS + "&sensor=false&key=" + GOOGLE_API_KEY
    response_dict = requests.get(url).json()
    random_index = random.randint(0,len(response_dict['results']) - 1)
    random_item = response_dict['results'][random_index]
    return process_location(random_item)

def process_location(random_item):
    c = {}
    c['lat'] = random_item['geometry']['location']['lat']
    c['long'] = random_item['geometry']['location']['lng']
    c['icon'] = random_item['icon']
    c['name'] = random_item['name']
    c['address'] = random_item['vicinity']
    if 'photos' in random_item:
        photo_ref = random_item['photos'][0]['photo_reference']
        photo_link = GOOGLE_PHOTO + photo_ref + "&sensor=false&key=" + GOOGLE_API_KEY + "&maxheight=300"
    else:
        photo_link = "N/A"
    c['photo'] = photo_link
    return c

def random_event(lat,lng):
    url = NEW_YORK_TIMES_BASE_STRING + "&ll=" + str(lat) + "," + str(lng) + "&radius=1000&limit=10"
    event_results = requests.get(url).json()
    if len(event_results['results']) == 0:
        return process_event(event_results, True)
    random_index = random.randint(0,len(event_results['results']) - 1)
    random_item = event_results['results'][random_index]
    return process_event(random_item, False)


def process_event(result, filler):
    if (filler == False):
        event = {}
        event['id'] = result['event_id']
        event['name'] = result['event_name']
        event['link'] = result['event_detail_url']
        if "venue_name" in result:
            event['location'] = result['venue_name']
        else:
            event['location'] = "N/A"
        description = html2text.html2text(result['web_description'])
        event['description'] = description
        if 'telephone' in result:
            event['phone_number'] = result['telephone']
        else:
            event['phone_number'] = "N/A"
        event['street_address'] = result['street_address']
        event['city'] = result['city']
        event['state'] = result['state']
        if 'postal_code' in result:
            event['postal_code'] = result['postal_code']
        else:
            event['postal_code'] = "N/A"
        return event
    else:
        event = {}
        event['id'] = "id"
        event['name'] = "name"
        event['link'] = "link"
        event['location'] = "location"
        event['description'] = "description"
        event['phone_number'] = "phone_number"
        event['street_address'] = "street_address"
        event['city'] = "city"
        event['state'] = "state"
        event['postal_code'] = "postal_code"
        return event

if __name__ == "__main__":
    app.debug = True
    app.run()

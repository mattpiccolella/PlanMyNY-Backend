from flask import Flask, jsonify
import requests, random, html2text
from string import replace

app = Flask(__name__)

ORDR_IN_BASE_STRING = "https://r-test.ordr.in/"
ORDR_IN_SECRET = "mt5rsSaIPd7SZDqjKg8rNSTTJ9LhKOCnm1c8nbGn_VY"
ORDR_IN_AUTH = "/?_auth=1," + ORDR_IN_SECRET

@app.route("/v1.0/random_restaurant/<street_address>/<city>/<zip_code>/<price>")
def place_order(street_address,city,zip_code,price):
    this_item = random_item(street_address,city,zip_code,price)
    if 'failed' in this_item:
        c = {}
        c['failed'] = True
        return jsonify(c)
    else:
        c = {}
        if 'descrip' in this_item['item']:
            c['description'] = this_item['item']['descrip']
        if 'price' in this_item['item']:
            c['price'] = this_item['item']['price']
        if 'name' in this_item['item']:
            c['name'] = this_item['item']['name']
        if 'na' in this_item['restaurant']:
            c['restaurant'] = this_item['restaurant']['na']
        if 'cu' in this_item['restaurant']:
            c['types'] = this_item['restaurant']['cu']
        if 'addr' in this_item['restaurant']:
            c['address'] = this_item['restaurant']['addr']
        return jsonify(c)

def random_item(street_address,city,zip_code, price):
    menu_response = random_menu(street_address,city,zip_code)
    x = 0
    lower_bound = float(price) * .8
    upper_bound = float(price) * 1.2
    ordered = False
    while (True):
        random_item = menu_response['menu_response']['menu'][random.randint(0,len(menu_response['menu_response']['menu']) - 1)]
        if 'children' in random_item:
            random_sub_item = random_item['children'][random.randint(0,len(random_item['children'])-1)]
            price = float(random_sub_item['price'])
            if ((price > lower_bound and price < upper_bound) and random_sub_item['is_orderable'] == "1" and not ('children' in random_sub_item)):
                c = {}
                c['item'] = random_sub_item
                c['restaurant'] = menu_response['restaurant']
                return c
            else:
                x = x + 1
                if (x % 100 == 0):
                    menu_response = random_menu(street_address,city,zip_code)
                    if (x > 500000):
                        break
        else:
            x = x+1
            if (x > 500000):
                break
    c = {}
    c['failed'] = True
    return c

def random_menu(street_address,city,zip_code):
    restaurant_url = ORDR_IN_BASE_STRING + "dl/ASAP" + "/" + str(zip_code) + "/" + city + "/" + street_address + ORDR_IN_AUTH
    restaurant_url = restaurant_url.replace(" ", "%20")
    response = requests.get(restaurant_url).json()
    random_index = random.randint(0,len(response) - 1)
    selected_restaurant = response[random_index]
    menu_url = ORDR_IN_BASE_STRING + "/rd/" + str(selected_restaurant['id']) + ORDR_IN_AUTH
    menu_response = requests.get(menu_url).json()
    c = {}
    c['restaurant'] = selected_restaurant
    c['menu_response'] = menu_response
    return c

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

GEOCODING_BASE_STRING = "http://maps.googleapis.com/maps/api/geocode/json?address="

@app.route("/")
def home():
    return "This is the backend API for the PlanMyNY iPhone application."

@app.route("/v1.0/random_trip")
def random_trip():
    c = {}
    location = random_location()
    event = random_event(location['lat'], location['long'])
    restaurant = random_restaurant(event)
    c['location'] = location
    c['event'] = event
    c['restaurant'] = restaurant
    response = jsonify(c)
    return response

def random_restaurant(event):
    address = event['street_address'] + ", " + event['city'] + ", " + event['state']
    address = address.replace(" ", "+")
    coord_query = GEOCODING_BASE_STRING + address +"&sensor=false"
    coord_results = requests.get(coord_query).json()
    if (len(coord_results) == 0):
        return "ERROR"
    location = coord_results["results"][0]
    lat = location['geometry']['location']['lat']
    lng = location['geometry']['location']['lng']
    return process_restaurant(lat,lng)

def process_restaurant(lat,lng):
    query_string = GOOGLE_PLACES_BASE_STRING + str(lat) + "," + str(lng) + "&types=restaurant&key=" + GOOGLE_API_KEY + "&radius=1000&sensor=false"
    results = requests.get(query_string).json()
    if (len(results['results']) == 0):
        return "ERROR"
    rand_index = random.randint(0,len(results['results'])-1)
    result = results['results'][rand_index]
    name = result['name']
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']
    address = result['vicinity']
    if 'ranking' in result:
        ranking = result['rating']
    else:
        ranking = "N/A"
    if 'photos' in result:
        photo_reference = result['photos'][0]['photo_reference']
    else:
        photo_reference = "N/A"
    reference = result['reference']
    details_string = GOOGLE_DETAILS_BASE_STRING + reference + "&key=" + GOOGLE_API_KEY + "&sensor=false"
    details = requests.get(details_string).json()
    if 'result' in details:
        detail = details['result']
        if 'website' in detail:
            website = detail['website']
        else:
            website = "N/A"
    else:
        website = "N/A"
    if 'price_level' in result:
        price = result['price_level']
    else:
        price = "N/A"
    new_restaurant = {}
    new_restaurant['name'] = name
    new_restaurant['website'] = website
    new_restaurant['address'] = address
    new_restaurant['reference'] = reference
    new_restaurant['ranking'] = ranking
    new_restaurant['price'] = price
    if photo_reference != "N/A":
        photo_link = GOOGLE_PHOTO + photo_reference+ "&key=" + GOOGLE_API_KEY + "&sensor=false&maxheight=200"
        new_restaurant['photo'] = photo_link
    else:
        new_restaurant['photo'] = "ERROR"
    return new_restaurant
        

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

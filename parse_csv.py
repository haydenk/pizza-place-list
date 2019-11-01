from csv import DictReader, DictWriter
from geojson import Feature, Point, FeatureCollection
from requests import post
from json import loads, dump
from os import environ

api_key = environ.get('MAPQUEST_API_KEY') 
mapquest_url = "http://www.mapquestapi.com/geocoding/v1/address?key={api_key}".format(api_key=api_key)


def read_csv_data_file(filename):
    data = []
    csv_reader = DictReader(open(filename, 'r'))
    for csv_row in csv_reader:
        data.append(csv_row)
    return data


dallas = read_csv_data_file("data/dallas.csv")

features = []

for row in dallas:
    status = row.get('status', 'new').lower()
    if status == 'new' or status == 'update':
        row['status'] = 'processed'
        post_data = {
            "location": "{address}, {city_state_zip}".format(address=row.get('address'),
                                                             city_state_zip=row.get('city_state_zip'))
        }
        address_lookup_response = post(mapquest_url, post_data)
        if address_lookup_response.status_code == 200:
            json_data = loads(address_lookup_response.content)
            lat_lng = json_data.get('results')[0].get('locations')[0].get('latLng')
            row['lat'] = lat_lng.get('lat')
            row['lng'] = lat_lng.get('lng')

            feature_properties = {
                "marker-symbol": "restaurant",
                "name": row.get('name'),
                "address": row.get('address'),
                "city_state_zip": row.get('city_state_zip'),
                "phone": row.get('phone'),
            }
            feature = Feature(geometry=Point((lat_lng.get('lng'), lat_lng.get('lat'))),
                              properties=feature_properties)
            features.append(feature)
            feature_collection = FeatureCollection(features)
            with open('maps/dallas.geojson', 'w') as geo_json:
                dump(feature_collection, geo_json)

header = dallas[0].keys()
with open('data/dallas.csv', 'w') as csv_file:
    writer = DictWriter(csv_file, header)
    writer.writeheader()
    for d in dallas:
        writer.writerow(d)


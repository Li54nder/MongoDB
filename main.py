import csv
import json
from collections import OrderedDict
from datetime import datetime
from types import SimpleNamespace
from pymongo import MongoClient
import time


NONE_VALUES = ["", " ", "Unknown", "unknown"]


header_names = ('source_name', 'source_link', 'event_id', 'event_date', 'event_title', 'event_description', 'location_description', 'location_accuracy', 'landslide_category', 'landslide_trigger', 'landslide_size',
                'fatality_count', 'injury_count', 'country_name', 'country_code', 'gazeteer_closest_point', 'gazeteer_distance', 'submitted_date', 'created_date', 'last_edited_date', 'longitude', 'latitude')


entries = []
with open('Global_Landslide_Catalog.csv', 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file, header_names)
    first_line = True
    for row in reader:
        if first_line:
            first_line = False
            continue

        entry = OrderedDict()

        entry['_id'] =              int(row['event_id'])
        entry['date'] =             None if row['event_date'] in NONE_VALUES else datetime.fromtimestamp(time.mktime(datetime.strptime(row['event_date'], '%m/%d/%Y %I:%M:%S %p').timetuple())).isoformat()
        entry['title'] =            row['event_title']
        entry['description'] =      row['event_description']
        entry['category'] =         row['landslide_category']
        entry['trigger'] =          row['landslide_trigger']
        entry['size'] =             row['landslide_size']
        entry['fatality_count'] =   0 if row['fatality_count'] in NONE_VALUES else int(row['fatality_count'])
        entry['injury_count'] =     0 if row['injury_count'] in NONE_VALUES else int(row['injury_count'])

        location = OrderedDict()
        location['latitude'] =      row['latitude']
        location['longitude'] =     row['longitude']
        location['accuracy'] =      None if row['location_accuracy'] in NONE_VALUES else 0 if row['location_accuracy'] == "exact" else int(row['location_accuracy'].split('km')[0])
        location['description'] =   row['location_description']

        country = OrderedDict()
        country['code'] =           row['country_code']
        country['name'] =           row['country_name']

        location['country'] =       country

        entry['location'] =         location

        closest_gazeteer = OrderedDict()
        closest_gazeteer['name'] =      row['gazeteer_closest_point']
        closest_gazeteer['distance'] =  row['gazeteer_distance']
        entry['closest_gazeteer'] =     closest_gazeteer

        archiving = OrderedDict()
        archiving['submitted_date'] =   None if row['submitted_date'] in NONE_VALUES else datetime.fromtimestamp(time.mktime(datetime.strptime(row['submitted_date'], '%m/%d/%Y %I:%M:%S %p').timetuple())).isoformat()
        archiving['created_date'] =     None if row['created_date'] in NONE_VALUES else datetime.fromtimestamp(time.mktime(datetime.strptime(row['created_date'], '%m/%d/%Y %I:%M:%S %p').timetuple())).isoformat()
        archiving['last_edited_date'] = None if row['last_edited_date'] in NONE_VALUES else datetime.fromtimestamp(time.mktime(datetime.strptime(row['last_edited_date'], '%m/%d/%Y %I:%M:%S %p').timetuple())).isoformat()
        entry['archiving'] = archiving

        source = OrderedDict()
        source['name'] = row['source_name']
        source['link'] = row['source_link']
        entry['source'] = source

        entries.append(entry)


output = {
    "Landslide": entries
}


with open('Landslide.json', 'w') as json_file:
    json.dump(output, json_file)
    json_file.write('\n')


# json_data = None
# with open('Landslide.json', 'r') as json_file:
#     data = json_file.read()
#     json_data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


client = MongoClient('localhost', 27017)
db = client['LandslideDB']
collection = db['Landslide']
# print(json_data.Landslide)
collection.insert_many(output['Landslide'])
import os
import json
import spacy
import geopy.distance
from geopy.geocoders import Nominatim

class Caption:
    caption = None
    locs = None

    address = None
    coords = None

    toponym_true_pos = 0
    toponym_false_pos = 0
    toponym_false_neg = 1

    location_true_pos = 0
    location_false_pos = 0
    location_false_neg = 1

    def __init__(self, json_object):
        self.caption = json_object["caption"]
        self.expected_toponym = json_object["ground truth toponym"]
        self.locs = []

        address = json_object["disambiguated"]
        coords = (json_object["guide-latitude-WGS84"], json_object["guide-longitude-WGS84"])

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.caption)

        for ent in doc.ents:
            if ent.label_ in ["FAC", "GPE", "LOC"]:
                self.locs.append(Toponym(string=ent.text))

        for loc in self.locs:
            if loc.toponym == self.expected_toponym:
                loc.toponym_true_pos = True
                self.toponym_true_pos = 1
                self.toponym_false_neg = 0
            else:
                loc.toponym_true_pos = False
                self.toponym_false_pos += 1

            if geopy.distance.distance(self.coords, loc.coords).km < 20:
                loc.location_true_pos = True
                self.location_true_pos = 1
                self.location_false_neg = 0
            else:
                loc.location_true_pos = False
                self.location_false_pos += 1

    def __str__(self):
        ret_str = ""

        if len(self.locs) == 0:
            ret_str += "The caption '" + self.caption + "' contains no identifiable toponyms:\n"
        else:
            ret_str += "The caption '" + self.caption + "' contains the following toponyms:\n"
            for loc in self.locs:
                ret_str += str(loc)
            ret_str += "This caption had " + str(self.toponym_true_pos) + " true positive(s), " + str(self.toponym_false_pos) + " false positive(s) and " + str(self.toponym_false_neg) + " false negative(s)\n"

        return ret_str


class Toponym:
    toponym = None

    address = None
    coords = None

    toponym_true_pos = None
    location_true_pos = None
    

    def __init__(self, string):
        self.toponym = string

        geolocator = Nominatim(user_agent="coursework")
        prediction = geolocator.geocode(self.toponym, limit=1)

        self.address = prediction.address,
        self.coords = (prediction.latitude, prediction.longitude)

    def __str__(self):
        ret_str = "The toponym '" + self.toponym + "' located at: " + str(self.coords) + str(self. address) + "\n"
        if self.toponym_true_pos is not None:
            ret_str += "This toponym is considered a " + str(self.toponym_true_pos) + " positive for the caption\n"
        if self.toponym_true_pos is not None:
            ret_str += "This location is considered a " + str(self.location_true_pos) + " positive for this toponym\n"

        return ret_str



def read_caps(file_name):
    caps = []

    with open(file_name, "r") as file:
        data = json.load(file)

    for loc in data:
        caps.append(Caption(loc))

    return caps

if __name__ == "__main__":
    caps = read_caps("json-capLatLong.json")
    for cap in caps:
        print(cap)
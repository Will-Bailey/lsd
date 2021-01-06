import os
import json
import spacy
import random
import geopy.distance
from spacy.kb import KnowledgeBase
from geopy.geocoders import Nominatim

class Caption:
    caption = None
    toponyms = None

    address = None
    coords = None

    toponym_true_pos = 0
    toponym_false_pos = 0
    toponym_false_neg = 1

    location_true_pos = 0
    location_false_pos = 0
    location_false_neg = 1

    def __init__(self, json_object, improved_ner=False, get_locs=True, first_loc=True):
        self.caption = json_object["caption"]
        self.expected_toponym = json_object["ground truth toponym"]
        self.toponyms = []

        self.address = json_object["disambiguated"]
        self.coords = (json_object["guide-latitude-WGS84"], json_object["guide-longitude-WGS84"])

        if improved_ner:
            nlp = get_improved_ner()
        else:
            nlp = spacy.load("en_core_web_sm")

        doc = nlp(self.caption)


        for ent in doc.ents:
            if ent.label_ in ["FAC", "GPE", "LOC"]:
                self.toponyms.append(Toponym(cap=self, string=ent.text, get_locs=get_locs, first_loc=first_loc))

        for loc in self.toponyms:
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

        if len(self.toponyms) == 0:
            ret_str += "The caption '" + self.caption + "' contains no identifiable toponyms:\n"
        else:
            ret_str += "The caption '" + self.caption + "' contains the following toponyms:\n"
            for loc in self.toponyms:
                ret_str += str(loc)
            ret_str += "This caption had " + str(self.toponym_true_pos) + " true positive(s), " + str(self.toponym_false_pos) + " false positive(s) and " + str(self.toponym_false_neg) + " false negative(s)\n"

        return ret_str


class Toponym:
    toponym = None

    address = None
    coords = None
    distance = None

    toponym_true_pos = None
    location_true_pos = None
    

    def __init__(self, cap, string, get_locs=True, first_loc=True):
        self.toponym = string

        if get_locs:
            shortest_distance = None

            if first_loc:
                limit = 1
            else:
                limit = 20

            geolocator = Nominatim(user_agent="coursework")
            predictions = geolocator.geocode(self.toponym, exactly_one=False, limit=limit)

            for prediction in predictions:
                distance = geopy.distance.distance(cap.coords, (prediction.latitude, prediction.longitude)).km
                if shortest_distance is None or distance < shortest_distance:
                    closest = prediction
                    shortest_distance = distance
                    self.distance = shortest_distance

                    self.address = prediction.address,
                    self.coords = (prediction.latitude, prediction.longitude)


    def __str__(self):
        ret_str = "The toponym '" + self.toponym + "' located at: " + str(self.coords) + str(self. address) + "\n"
        if self.toponym_true_pos is not None:
            ret_str += "This toponym is considered a " + str(self.toponym_true_pos) + " positive for the caption\n"
        if self.toponym_true_pos is not None:
            ret_str += "This location is considered a " + str(self.location_true_pos) + " positive for this toponym\n"

        return ret_str



def read_caps(file_name, improved_ner=False, get_locs=True, first_loc=True):
    caps = []

    with open(file_name, "r") as file:
        data = json.load(file)

    for loc in data:
        caps.append(Caption(loc, improved_ner=improved_ner, get_locs=get_locs, first_loc=first_loc))

    return caps

def train(train_data, test=False):
    nlp = spacy.load("en_core_web_sm")
    ner = nlp.get_pipe("ner")

    if test:
        test_train_data(train_data)    

    for caption, annotations in train_data:
        for ent in annotations["entities"]:
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimiser = nlp.begin_training()
        for i in range(100):
            random.shuffle(train_data)
            for caption, annotations in train_data:
                nlp.update([caption], [annotations], drop=0.6, sgd=optimiser, losses={})

    nlp.to_disk("my_model")

def test_train_data(train_data):
    for data in train_data:
        for entity in data[1]["entities"]:
            print(data[0][entity[0]:entity[1]])

def get_improved_ner():
    load_dir = "my_model"

    if not os.path.isdir(load_dir):
        train_data = [
                ("Farm track south of Wickwar", {"entities": [(20, 27, 'GPE')]}),
                ("Farm track north of Yate", {"entities": [(20, 24, 'GPE')]}),
                ("Long barrow west of North Nibley", {"entities": [(20, 32, 'GPE')]}),
                ("Long barrow near Wotton", {"entities": [(17, 23, 'GPE')]}),
                ("A483 east of Evesham", {"entities": [(13, 20, 'GPE')]}),
                ("A483 east of Worcester", {"entities": [(13, 22, 'GPE')]}),
                ("Power Line south of Wickwar", {"entities": [(20, 27, 'GPE')]}),
                ("Power Line south of Yate", {"entities": [(20, 24, 'GPE')]})
            ]
        train(train_data)

    return spacy.load("my_model")

if __name__ == "__main__":
    caps = read_caps("json-capLatLong.json", get_locs=False)
    true_pos = 0
    false_pos = 0
    false_neg = 0

    out_str = ""

    for cap in caps:
        out_str += "Caption: " + cap.caption
        
        if len(cap.toponyms) == 0:
            out_str += ", no entities detected "
        else:
            out_str += ", Entities: "
            for toponym in cap.toponyms:
                out_str += toponym.toponym + ", "

        true_pos += cap.toponym_true_pos
        false_pos += cap.toponym_false_pos
        false_neg += cap.toponym_false_neg

        out_str += "\n"

    precision = true_pos/(true_pos + false_pos)
    recall = true_pos / len(caps)
    f1 = 2 * precision * recall / (precision + recall)

    out_str += "True Positive(s): " + str(true_pos) + "\n"
    out_str += "False Positive(s): " + str(false_pos) + "\n"
    out_str += "False Negative(s): " + str(false_neg) + "\n"
    out_str += "Precision: " + str(precision) + "\n"
    out_str += "Recall: " + str(recall) + "\n"
    out_str += "F1: " + str(f1) + "\n"

    print(out_str)
import os
import json
import datetime

def get_jsons(dir="unformatted_fitbit_data"):
    json_dict = {}
    for person in os.scandir(dir):
        json_dict[person.name] = {}
        for metric in os.scandir(person):
            json_dict[person.name][metric.name] = []
            for file in os.scandir(metric):
                with open(file, "r") as read_file:
                    json_dict[person.name][metric.name].append(json.load(read_file))
    return json_dict

def sanatise_jsons(json_dict):
    new_dict = {}
    for person in json_dict.keys():
        new_dict[person] = {}
        for metric in json_dict[person].keys():
            for file in json_dict[person][metric]:
                for point in file:
                    items = list(point.items())
                    if items[0][1] not in new_dict[person].keys():
                        new_dict[person][items[0][1]] = {}
                    new_dict[person][items[0][1]][metric] = items[1][1]
    return new_dict


def write_jsons(json_dict):
    for person in json_dict.keys():
        # set up the file structure
        if not os.path.exists("data/"):
            os.makedirs("data/")
        with open("data/" + person + ".json", "w"):
            pass

        with open("data/" + person + ".json", "a") as json_file:
            json.dump(json_dict[person], json_file, indent=2)

json_dict = get_jsons()
json_dict = sanatise_jsons(json_dict)
write_jsons(json_dict)
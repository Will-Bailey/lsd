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
            new_dict[person][metric] = []
            for file in json_dict[person][metric]:
                for point in file:
                    for attribute, value in point.items():
                        if attribute == "dateTime":
                            new_dateTime = datetime.datetime.strptime(value, '%m/%d/%y %H:%M:%S').isoformat()
                        elif attribute == "value":
                            new_value = float(value)
                    new_dict[person][metric].append({"dateTime":new_dateTime, "value":new_value})
    return new_dict


def write_jsons(json_dict):
    make_file_structure()
    for person in json_dict.keys():
        for metric in json_dict[person].keys():
            with open("data/" + person + "/" + metric + ".json", "a") as json_file:
                for point in json_dict[person][metric]:
                    json.dump(point, json_file, indent=2)

def make_file_structure():
    for person in json_dict.keys():
        if not os.path.exists("data/"+ person):
            os.makedirs("data/" + person)
        for metric in json_dict[person].keys():
            if not os.path.exists("data/" + person + "/" + metric + ".json"):
                with open("data/" + person + "/" + metric + ".json", "w"):
                    pass


json_dict = get_jsons()
json_dict = sanatise_jsons(json_dict)
write_jsons(json_dict)
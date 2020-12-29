from geopy.geocoders import Nominatim
from question1 import get_entities, analyse_results
import geopy.distance

def get_coords(dicts):
    geolocator = Nominatim(user_agent="coursework")
    coords = {}

    for dict in dicts:
        dict["predictions"] = []
        for loc in dict["location_entities"]:
            prediction = {}
            
            predicted_loc = geolocator.geocode(loc, limit=1)
            prediction["coords"] = (predicted_loc.latitude, predicted_loc.longitude)
            prediction["address"] = predicted_loc.address
            
            dict["predictions"].append(prediction)

    return dicts

def analyse_coords(dicts):
    new_dicts = []
    accurate_predictions = 0
    total_predictions = 0

    for dict in dicts:
        if dict["false_neg"] > 0:
            dict["predictions"] = []

            prediction = {}
            prediction["true_pos"] = 0
            prediction["false_pos"] = dict["false_pos"]
            prediction["false_neg"] = dict["false_neg"]

            dict["predictions"].append(prediction)

        else :
            true_pos, false_pos, false_neg = 0, 0, 0
            expected_coords = dict["expected_coords"]
            
            for prediction in  dict["predictions"]:
                predicted_coords = prediction["coords"]

                total_predictions += 1
                prediction["error"] = geopy.distance.distance(predicted_coords, expected_coords).km

                if prediction["error"] <= 20:
                    true_pos += 1
                    accurate_predictions += 1
                else:
                    false_pos += 1

                prediction["true_pos"], prediction["false_pos"], prediction["false_neg"] = true_pos, false_pos, false_neg
        
        new_dicts.append(dict)
    return new_dicts


def main(file_name="json-capLatLong.json"):
    dicts = analyse_results(get_entities(file_name))
    dicts = get_coords(dicts)
    dicts = analyse_coords(dicts)

    for dict in dicts:
        for prediction in dict["predictions"]:
            print(str(prediction["address"]) + ", " + str(prediction["coords"]) + ", " + str(prediction["true_pos"]) + ", " + str(prediction["false_pos"]) + ", " + str(prediction["false_neg"]))

if __name__ == "__main__":
    main()
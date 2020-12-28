import os
import json
import spacy
import sys

def get_entities(file_name):
    ret_dicts = []
    nlp = spacy.load("en_core_web_sm")
    with open(file_name, "r") as file:
        data = json.load(file)

    # Build the basics from the JSON file
    for loc in data:
        doc = nlp(loc["caption"])
        ents = []
        
        for ent in doc.ents:
            if ent.label_ in ["FAC", "GPE", "LOC"]:
                ents.append(ent.text)

        ret_dicts.append({"caption": loc["caption"], "locaiton_entities": ents, "expected_entity": loc["ground truth toponym"]})

    return ret_dicts

def analyse_results(dicts):
    # Perform an analysis of false positives and negatives etc.
    accurate_predictions = 0
    total_predictions = 0

    for dict in dicts:
        true_pos, false_pos, false_neg = 0, 0, 0

        if dict["expected_entity"] in dict["locaiton_entities"]:
            true_pos += 1
            accurate_predictions += 1
        else:
            false_neg += 1

        for loc in dict["locaiton_entities"]:
            total_predictions += 1
            if loc != dict["expected_entity"]:
                false_pos += 1

        dict["true_pos"], dict["false_pos"], dict["false_neg"] = true_pos, false_pos, false_neg


    precision = accurate_predictions / total_predictions
    recall = accurate_predictions / len(dicts)
    f1 = 2 * precision * recall / (recall + precision)

    metrics = {"precision": precision, "recall": recall, "F1": f1}

    return metrics

def main():
    assert len(sys.argv) == 2, "Please pass the name of the JSON file to be inspected."

    dicts = get_entities(sys.argv[1])
    metrics = analyse_results(dicts)

    print("Line format:\nCaption, [location entities], True Positives, False Positives, False Negatives\n")

    for dict in dicts:
        print(dict["caption"] + ", " + str(dict["locaiton_entities"]) + ", " + str(dict["true_pos"]) + ", " + str(dict["false_pos"]) + ", " + str(dict["false_neg"]))

    print("Precision: ", metrics["precision"])
    print("Recall: ", metrics["recall"])
    print("F1: ", metrics["F1"])

if __name__ == "__main__":
    main()
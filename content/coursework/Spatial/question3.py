from question1 import *

if __name__ == "__main__":
    caps = read_caps("json-capLatLong.json", improved_ner=True)
    true_pos = 0
    false_pos = 0
    false_neg = 0

    out_str = ""

    for cap in caps:
        out_str += "Caption: " + cap.caption
        
        if len(cap.toponyms) == 0:
            out_str += ", no entities detected "
        else:
            out_str += ", Locations: "
            for toponym in cap.toponyms:
                out_str += str(toponym.address) + ", "
                out_str += str(toponym.coords) + ", "
                out_str += str(toponym.distance)

        true_pos += cap.location_true_pos
        false_pos += cap.location_false_pos
        false_neg += cap.location_false_neg

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
from question1 import *
import csv

if __name__ == "__main__":
    caps = read_caps("json-capLatLong.json", improved_ner=True, first_loc=False)
    with open("out.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter = ",")
        writer.writerow(["CAPTION", "LONGITUDE", "LATITUDE"])

        for cap in caps:
            for toponym in cap.toponyms:
                writer.writerow([cap.caption, toponym.coords[0], toponym.coords[1]])

    test=False
    if test:
        with open("test.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter = ",")
            writer.writerow(["CAPTION", "LATITUDE", "LONGITUDE"])

            for cap in caps:
                for toponym in cap.toponyms:
                    writer.writerow([cap.caption, cap.coords[0], cap.coords[1]])

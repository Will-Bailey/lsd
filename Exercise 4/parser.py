import spacy
import json
import os

nlp = spacy.load("en_core_web_sm")
infile = open('JackHagelExerciseText-NotEscaped.txt', "r")
theText = infile.read()
infile.close()

doc = nlp(theText)

for ent in doc.ents:
	place = ent.text
	print ("Geo-place: " + str(place) + " " + str(ent.label_))
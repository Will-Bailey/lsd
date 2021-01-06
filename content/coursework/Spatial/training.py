import random
import spacy

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
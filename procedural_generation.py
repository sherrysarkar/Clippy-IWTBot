import json
import itertools
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import neural_network

def parse_data():
    with open('dataset.json') as data_file:
        data = json.load(data_file)
    templates = []
    labels = []
    for i in range(len(data)):
        templates.append(data[i]["template"])
        labels.append(data[i]["label"])

    # find the length of each subtemplate. [1, 2, 3, 4] [1, 2, 3] [1, 2] -> [1, 1, 1], [1, 1, 2], [
    # [1 ,2] -> [[1], [2]],,, [[1, 2][1, 2, 3]] -> [[1], [2]]

    X = []
    Y = []
    for j, template in enumerate(templates):
        for element in itertools.product(*template):
            sentence = ""
            for number, word in enumerate(element):
                sentence += word
                if number != len(element) - 1:
                    sentence += " "
            s = sentence.lower()
            ## S is the setence, here is a word.
            X.append([s])
            Y.append(labels[j])

    return X, Y

X, Y = parse_data()




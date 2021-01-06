import pymongo
import pprint

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["question1"]
collection = db["fitbit_data"]

pipeline = [
    {
        '$project': {
            '_id': 0, 
            'dateTime': 1, 
            'day': {
                '$toInt': {
                    '$substr': [
                        '$dateTime', 8, 2
                    ]
                }
            }, 
            'month': {
                '$toInt': {
                    '$substr': [
                        '$dateTime', 5, 2
                    ]
                }
            }, 
            'steps1': '$person_1_fitbit.steps', 
            'steps2': '$person_2_fitbit.steps'
        }
    }, {
        '$match': {
            'month': {
                '$eq': 6
            }
        }
    }, {
        '$group': {
            '_id': '$day', 
            'steps1sum': {
                '$sum': '$steps1'
            }, 
            'steps2sum': {
                '$sum': '$steps2'
            }
        }
    }, {
        '$sort': {
            '_id': 1
        }
    }
]

pprint.pprint(list(collection.aggregate(pipeline)))
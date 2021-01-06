import pymongo
import pprint

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["question1"]
collection = db["fitbit_data"]

pipeline = [
    {
        '$project': {
            'dateTime': 1, 
            'person_1_fitbit': 1, 
            'person_2_fitbit': 1
        }
    }, {
        '$addFields': {
            'hour': {
                '$toInt': {
                    '$substr': [
                        '$dateTime', 11, 2
                    ]
                }
            }, 
            'morning': {
                '$and': [
                    {
                        '$gte': [
                            '$hour', 7
                        ]
                    }, {
                        '$lte': [
                            '$hour', 12
                        ]
                    }
                ]
            }, 
            'day': {
                '$and': [
                    {
                        '$gte': [
                            '$hour', 13
                        ]
                    }, {
                        '$lte': [
                            '$hour', 19
                        ]
                    }
                ]
            }, 
            'night': {
                '$not': [
                    {
                        '$or': [
                            '$morning', '$day'
                        ]
                    }
                ]
            }
        }
    }, {
        '$project': {
            'hour': 0
        }
    }, {
        '$out': 'fitbit_data'
    }
]

pprint.pprint(list(collection.aggregate(pipeline)))
import json
from pymongo import MongoClient

host_name ='' #put your host name here

if __name__ == '__main__':
    fin = open("distribution.txt", "r")
    distribution = json.loads(fin.read())
    fin.close()
    client = MongoClient(host_name)
    db = client['701']
    distribution_collection = db.distribution
    distribution_collection.insert(distribution)
    client.close()

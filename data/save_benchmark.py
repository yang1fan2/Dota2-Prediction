import requests 
import json
import os, logging, argparse
from six.moves import cPickle
from pymongo import MongoClient
from time import sleep
from sys import exit

client = MongoClient('yangyifans-MacBook-Pro.local')#MongoClient('localhost', 27017)
db = client['701']
benchmark_collection = db.benchmark

benchmark_url = 'https://api.opendota.com/api/benchmarks?hero_id='

min_match = 30
if __name__ == '__main__':
    for i in range(1,114,1):
        benchmark = json.loads(requests.get(benchmark_url+str(i)).content)
        if benchmark_collection.find_one({'hero_id':benchmark['hero_id']}) != None:
            continue
        benchmark_collection.insert(benchmark)
        if i%10==0:
            print i 
        
    
    #print requests.get(url).content
    
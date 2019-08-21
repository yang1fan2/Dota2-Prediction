import json
import os, logging, argparse
from six.moves import cPickle
from pymongo import MongoClient
from time import sleep
from sys import exit

client = MongoClient()#MongoClient('localhost', 27017)
db = client['701']
hero_collection = db.hero

if __name__ == '__main__':

    fin = open("hero108.json","r")
    hero108 = json.loads(fin.read())
    fin.close()
    #print hero108

    if hero_collection.find_one({'ID':hero108['ID']}) == None:
        hero_collection.insert(hero108) 
    #print hero_list
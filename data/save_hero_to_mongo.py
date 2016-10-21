import json
import os, logging, argparse
from six.moves import cPickle
from pymongo import MongoClient
from time import sleep
from sys import exit

client = MongoClient('yangyifans-MacBook-Pro.local')#MongoClient('localhost', 27017)
db = client['701']
hero_collection = db.hero

if __name__ == '__main__':
    name_to_id = {}
    fin = open("hero_id.json","r")
    hero_id = json.loads(fin.read())['heroes']
    fin.close()
    for hero in hero_id:
        name_to_id[hero['localized_name'].lower()] = hero['id']
        name_to_id[hero['name'].lower()] = hero['id']


    fin = open("heros_attribute.json","r")
    hero_attribute = json.loads(fin.read())
    fin.close()
    #print len(hero_attribute)
    hero_list = []
    for k,v in hero_attribute.items():
        #print k,v
        v['Name'] = v['Name'].lower()
        v['ID'] = name_to_id[v['Name']]
        hero_list.append(v)
        #break
        if hero_collection.find_one({'ID':v['ID']}) != None:
            continue
        hero_collection.insert(v) 
    #print hero_list
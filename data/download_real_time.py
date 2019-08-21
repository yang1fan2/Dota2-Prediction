from multiprocessing import Pool
import requests 
import json
import os, logging, argparse
from six.moves import cPickle
from pymongo import MongoClient
from TorCtl import TorCtl
from sys import exit
from progress.bar import Bar
import random
import time


host_name = 'yangyifans-MacBook-Pro.local'#'yangyifans-MBP.wv.cc.cmu.edu'
replay_url = "https://api.opendota.com/api/replays?match_id="
post_url = "https://api.opendota.com/api/request/"
match_url ="https://api.opendota.com/api/matches/"

def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()

def load_dict(filename):
    fin = open(filename, 'rb')
    return cPickle.load(fin)

min_match = 100
num_process = 10

def download(match_id):
    client = MongoClient(host_name)
    db = client['701']
    realtime_collection = db.realtime
    db.access.update_one({'match_id': match_id}, {'$inc': {'count': 1}})
    
    while True:
        try:
            tmp = json.loads(requests.get(match_url+str(match_id)).content)
            if 'radiant_gold_adv' in tmp:
                break
            else:
                time.sleep(random.randint(3,5))
        except Exception, e:
            print 'match %s %d'%(e,match_id)
            time.sleep(random.randint(3,5))
    if tmp['radiant_gold_adv']==None:
        
        #pass
        return
    else:
        realtime_collection.insert(tmp)        
        client.close()
        return

    while True:
        try:
            post = json.loads(requests.post(post_url+str(match_id)).content)
            break
        except Exception, e:
            print 'post %s %d'%(e,match_id)
            time.sleep(random.randint(0,5))
    if not 'err' in post:
        print post
        client.close()
        return
    elif post['err']!=None:
        try:
            print tmp['err'], match_id
        except:
            pass
        client.close()
        return
    print 'post replay',match_id,post
    time.sleep(15)
    while True:
        try:
            tmp = json.loads(requests.get(match_url+str(match_id)).content)
            if 'radiant_gold_adv' in tmp:
                break
            else:
                time.sleep(random.randint(3,5))
        except Exception, e:
            print 'match %s %d'%(e,match_id)
            time.sleep(random.randint(0,5))
    if tmp['radiant_gold_adv']==None:
        print 'fail for the second time',match_id
    else:
        realtime_collection.insert(tmp)      
    client.close()  

if __name__ == '__main__':
    client = MongoClient(host_name)
    db = client['701']
    realtime_collection = db.realtime
    access_realtime = db.access
    match = load_dict("new_match.pk")
    match_list = []
    bar = Bar('Processing', max=len(match))  
    acc = {}
    for a in access_realtime.find():
        acc[a['match_id']] = a['count']
    match_dict = {}
    for m in realtime_collection.find({},{'match_id':1}):
        match_dict[m['match_id']]=1

    for i, m in enumerate(match):
        bar.next()
        match_id = int(m[-1])
        #if realtime_collection.find_one({'match_id':match_id}) != None:
         #   continue
        if match_id in match_dict:
            continue
        #if access_realtime.find_one({'match_id':match_id}) == None:
         #   access_realtime.insert({'match_id':match_id,"count":1})
        #acc = access_realtime.find_one({'match_id':match_id})
        if acc[match_id] >= 4:
            continue
        

        match_list.append(match_id)
    client.close()
    bar.finish()      
    random.shuffle(match_list)
    print 'loading match pickle finished'
    bar = Bar('Processing', max=len(match_list))        
    p = Pool(num_process)
    for i in p.imap(download,match_list):
        bar.next()
        #break
    bar.finish()        



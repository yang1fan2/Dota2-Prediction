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


player_profile_url = 'https://api.opendota.com/api/players/'

min_match = 100
num_process = 5

def get_player(account_id):
    client = MongoClient('yangyifans-MacBook-Pro.local')
    db = client['701']
    player_collection = db.player
    if player_collection.find_one({'account_id':account_id}) != None:
        client.close()
        return
    done =[0]*5
    player_profile = {}
    player_profile['account_id'] = account_id
    while True:
        try:
            for i in range(5):
                if i==0 and done[i] == 0:                    
                    tmp = json.loads(requests.get(player_profile_url+str(account_id)).content)
                    assert not "error" in tmp
                    done[i] = 1
                    for k,v in tmp.items():
                        player_profile[k] = v
                elif i==1 and done[i]==0:
                    player_wl = json.loads(requests.get(player_profile_url+str(account_id)+'/wl').content)
                    assert not "error" in player_wl
                    done[i] = 1
                    player_profile['win'] = player_wl['win']
                    player_profile['lose'] = player_wl['lose']
                elif i==2 and done[i]==0:
                    player_heroes = json.loads(requests.get(player_profile_url+str(account_id)+'/heroes').content)
                    assert not "error" in player_heroes
                    done[i] = 1
                    player_profile['heroes'] = player_heroes
                elif i==3 and done[i]==0:
                    player_heroes_rankings = json.loads(requests.get(player_profile_url+str(account_id)+'/rankings').content)
                    assert not "error" in player_heroes_rankings
                    done[i] = 1
                    player_profile['heroes_rankings'] = player_heroes_rankings
                elif i==4 and done[i]==0:
                    player_ratings = json.loads(requests.get(player_profile_url+str(account_id)+'/ratings').content)
                    assert not "error" in player_ratings
                    done[i] = 1
                    player_profile['ratings'] = player_ratings
            
            if sum(done)==5:
                break
        except Exception, e:
            cnt = random.randint(0, num_process/2)
            print 'error %s %d'%(e,account_id)
            if cnt==0:
#                conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="123456")
 #               conn.send_signal("NEWNYM")
  #              conn.close()
                pass
            else:
                time.sleep(random.randint(0,10))
            continue
    #print player_profile
    player_collection.insert(player_profile)
    client.close()

if __name__ == '__main__':
    fin = open("info.txt")
    player_list = []
    print 'starting '
    client = MongoClient('yangyifans-MacBook-Pro.local')

    db = client['701']
    player_collection = db.player

    for i,line in enumerate(fin.readlines()):
        if i<=2:
            continue
        if i%1000==0:
            print i
        account_id, count = map(int,line.strip().split())
        if player_collection.find_one({'account_id':account_id}) != None:
            continue
        player_list.append(account_id)
        if count < min_match:
            break
    print 'finish reading'
    client.close()
    num = len(player_list)   
    l = num/10              
    for idx in range(10):
        if idx==9:
            part = player_list[idx*l:]    
        else:
            part = player_list[idx*l:(idx+1)*l]
        print idx
        bar = Bar('Processing', max=len(part))
        p = Pool(num_process)
        for i in p.imap(get_player,part):
            bar.next()
        bar.finish()



        #break
    fin.close()

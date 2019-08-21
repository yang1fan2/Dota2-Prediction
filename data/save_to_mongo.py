from multiprocessing import Pool
import os, logging, argparse
from six.moves import cPickle
from pymongo import MongoClient
from time import sleep
from sys import exit
from progress.bar import Bar

client = MongoClient('yangyifans-MacBook-Pro.local')
db = client['701']
match_collection = db.matches
num_process = 100


def is_valid_match(gmd_result):
    '''Returns True if the given match details result should be considered,
    and False otherwise.'''
    for player in gmd_result['players']:
        if player['leaver_status'] is not 0:
            return False
    return True

def save_mongo(m):
    if not is_valid_match(m):
        return
    client = MongoClient('yangyifans-MacBook-Pro.local')
    db = client['701']
    match_collection = db.matches        
    match_id = m['match_id']
    if match_collection.find_one({'match_id':match_id}) != None:
        return
    match_collection.insert(m)
    client.close()


if __name__ == '__main__':
    list_dirs = os.walk("/Volumes/yang1fan2/dota/match_detail_very_high") 
    y = []
    x = []
    for root, dirs, files in list_dirs: 
        for f in files: 
            filename = os.path.join(root, f)
            if not "pk" in filename:
                continue
                   
            tmp = filename.split('/')[-1].split('.')[0]
            if tmp[0] <= '1':
                continue
            if (tmp[0]=='2') and (tmp[-1]<='7'):
                continue
            fin = open(filename,'rb')
            matches = cPickle.load(fin)
            fin.close()
            
            #bar = Bar('Processing', max=len(matches))
            #p = Pool(num_process)
            #for i in p.imap(save_mongo,matches):
             #   bar.next()
            # for m in matches:
            #     bar.next()
            #     if not is_valid_match(m):
            #         continue
            #     match_id = m['match_id']
            #     if match_collection.find_one({'match_id':match_id}) != None:
            #         continue
            #     match_collection.insert(m)

            #bar.finish()
            match_collection.insert(matches)
            print filename
            matches[:] = []
            
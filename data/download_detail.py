from TorCtl import TorCtl
import urllib2
import json
import dota2api
import cPickle
import time
from multiprocessing import Pool
import os
from six.moves import cPickle
import numpy as np
import random
from progress.bar import Bar
min_match = 100
num_process = 50

def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()



def retrieve(idx):
    
    while True:
        try:
            cnt = random.randint(0,len(api)-1)
            response = api[cnt].get_match_details(match_id=idx)
            #print '%d success'%idx
            break
        except Exception,e:
            #print "%s %d"%(e,idx)
            cnt = random.randint(0,num_process)
            if cnt==0:
                conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="123456")
                conn.send_signal("NEWNYM")
                conn.close()
            else:
                time.sleep(random.randint(0,10))

            
            continue
    return response

if __name__ == '__main__':
    api = [dota2api.Initialise("A0D097C39AFDA60C0A0B5F95DE85D348"),
            dota2api.Initialise("DA99B4A51376736C991FDADB1EB1488C")]
    list_dirs = os.walk("very_high") 
    y = []
    x = []
    match_cnt = 0
    player_counter = {}
    all_matches = []
    
    data = []
    filename = "very_high/9(100032).pk"
    fin = open(filename,'rb')
    matches = cPickle.load(fin)
    fin.close()
    print filename
    for m in matches:
        all_matches.append(m['match_id'])
    #all_matches = all_matches[:10000] 
    num = len(all_matches)   
    l = num/10              
    for idx in [0,1,2,3,7,8,9]:
        if idx==9:
            part = all_matches[idx*l:]    
        else:
            part = all_matches[idx*l:(idx+1)*l]
        bar = Bar('Processing', max=len(part))
        p = Pool(num_process)
        for i in p.imap(retrieve,part):
            bar.next()
            data.append(i)
            #print i
        bar.finish()
        #data = p.map(retrieve,all_matches)   
        f = open("match_detail_very_high/%s-%d.pk"%(filename.split('/')[1].split('.')[0],idx),"wb")
        cPickle.dump(data,f,protocol=cPickle.HIGHEST_PROTOCOL)
        data[:] = []
        f.close()    
    #break
    
    

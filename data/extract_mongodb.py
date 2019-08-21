import os
from pymongo import MongoClient
from progress.bar import Bar
#from progressbar import ProgressBar, Bar, Percentage, FormatLabel, ETA

from six.moves import cPickle
import numpy as np

def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()

def get_match_detail(m):
    w = m['radiant_win'] # whether radiant won
    radiant=[]
    dire = []
    for p in m['players']:
        if p['player_slot'] >= 128: # dire team
            dire.append(p['hero_id'])
        else:
            radiant.append(p['hero_id']) # radiant team
    if len(radiant)!=5 or len(dire)!=5:
        return (-1,-1)
    return (w,radiant + dire)

if __name__ == '__main__':
    client = MongoClient() 
    db = client['701']
    matches = db.matches
    N = matches.count()
    print N
    y = []
    x = []
    bar = Bar('Processing', max=N)
    for i, m in enumerate(matches.find()):
        bar.next()
        a,b = get_match_detail(m) 
        if a==-1:
            continue
        y.append(a)
        x.append(b)
    bar.finish()
    X = np.array(x) # features
    Y = np.array(y) # label

    N = X.shape[0]
    print 'number of examples = ',N
    train_x = X[:int(N*.9),:]
    train_y = Y[:int(N*.9)]
    valid_x = X[int(N*.9):int(N*.95),:]
    valid_y = Y[int(N*.9):int(N*.95)]
    test_x = X[int(N*.95):,:]
    test_y = Y[int(N*.95):]
    directory = "mongodb"
    save_as_pk((train_x, train_y),"%s/train.pk"%directory)
    save_as_pk((valid_x, valid_y),"%s/valid.pk"%directory)
    save_as_pk((test_x, test_y),"%s/test.pk"%directory)
    

    
    
import os, math
from pymongo import MongoClient
from progress.bar import Bar
#from progressbar import ProgressBar, Bar, Percentage, FormatLabel, ETA
from six.moves import cPickle
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import Imputer

def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()

def crawl_MMR_dist(dist):
    MMR_dist = [0] # 0-th element: number of players below those with MMR 0~99 = 0
    for bin in dist.find():
        MMR_dist.append(bin['cumulative_sum'])
    return MMR_dist

def crawl_account_ids(players):
    account_ids = set()
    bar = Bar('Crawling account ids', max = players.count())
    # Skip those players without profiles to prevent errors
    for p in players.find({'profile': {'$exists': True}}):
        bar.next()
        # print; print p['profile']['account_id']
        account_ids.add(p['profile']['account_id'])
    bar.finish()
    return account_ids

# format: [radiant1_MMR, radiant1_percentile, ..., dire5_MMR, dire5_percentile]
def extract_player_rank(m, thr, account_ids, players, MMR_dist):
    nonexistent_players = 0
    w = m['radiant_win'] # whether radiant won
    radiant = []
    dire = []
    total_players = MMR_dist[-1]

    for p in m['players']:
        MMR = 0
        percentile = 0  # based on Solo MMR
        id = p['account_id']

        # Check for non-existent players
        if id == 4294967295 or id not in account_ids:
            nonexistent_players += 1
            # Skip this match if non-existent players > threshold
            if nonexistent_players > thr:
                return (-1, -1)
            # Missing values: will impute with the average values later
            MMR = float('NaN')
            percentile = float('NaN')
        else:
            MMR = players.find_one({'account_id': id})['mmr_estimate']['estimate']
            percentile = float(MMR_dist[MMR // 100]) / float(total_players) * 100.0            
        # print (MMR, percentile)

        # player_slot: 0 ~ 5 for radiants, 128 ~ 132 for dires
        if p['player_slot'] >= 128:
            # dire team
            dire.append(MMR)
            dire.append(percentile)
        else:
            # radiant team
            radiant.append(MMR)
            radiant.append(percentile)

    if len(radiant) != 10 or len(dire) != 10:
        return (-1,-1)
    return (w, radiant + dire)

if __name__ == '__main__':
    # Parameters
    thr = 2;  # maximum tolerence threshold on the number of non-existent players in a match

    client = MongoClient()
    db = client['701']
    matches = db['matches']
    players = db['player']
    dist = db['distribution']
    y = []
    x = []

    MMR_dist = crawl_MMR_dist(dist)
    account_ids = crawl_account_ids(players)
    print str(len(account_ids)) + 'players with profiles and account ids'

    N = matches.count()
    print str(N) + ' matches found'
    N_extracted = 0

    bar = Bar('Extracting player-rank features in matches', max = N)
    for i, m in enumerate(matches.find()):
        bar.next()
        a,b = extract_player_rank(m, thr, account_ids, players, MMR_dist)
        # print; print b
        # Skip those matches with too many non-existent players or that are not 5 vs 5
        if a == -1:
            continue
        N_extracted += 1
        # print; print N_extracted
        y.append(a)
        x.append(b)
    bar.finish()

    N = X.shape[0]
    print 'Number of matches extracted: ' + str(N)
    print 'N_extracted = ' + str(N_extracted) # Just to verify the count
    X = np.array(x) # features
    Y = np.array(y) # label
    # Replace NaN with mean value
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)

    save_as_pk((X, Y), "player_rank.pk")
    

    
    
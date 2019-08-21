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

def crawl_ids_MMRs(players):
    # Put <account id, MMR> pair in a dictionary
    ids_MMRs = {}
    bar = Bar('Crawling account ids and MMRs', max = players.count())
    # Skip those players without profiles to prevent errors
    for p in players.find({'profile': {'$exists': True}}):
        bar.next()
        # print; print p['profile']['account_id']
        ids_MMRs[p['profile']['account_id']] = p['mmr_estimate']['estimate']
    bar.finish()
    return ids_MMRs

# Format: [radiant1_MMR, radiant1_percentile, ..., dire5_MMR, dire5_percentile] -> 20 dimensions
def extract_player_rank(m, thr, ids_MMRs, MMR_dist):
    nonexistent_players = 0
    y = m['radiant_win'] # whether radiant won
    radiant = []
    dire = []
    total_players = MMR_dist[-1]

    for p in m['players']:
        id = p['account_id']

        # Check for non-existent players
        if id == 4294967295 or not ids_MMRs.has_key(id):
            nonexistent_players += 1
            # Skip this match if non-existent players > threshold
            if nonexistent_players > thr:
                return (-1, -1)
            # Missing values: will impute with the average values later
            MMR = float('NaN')
            percentile = float('NaN')
        else:
            MMR = ids_MMRs[id]
            percentile = float(MMR_dist[MMR // 100]) / float(total_players) * 100.0  # based on Solo MMR
        # print (MMR, percentile)

        # player_slot: 0 ~ 5 for radiants, 128 ~ 132 for dires
        if p['player_slot'] >= 128:
            # dire team
            dire.append(float(MMR))
            dire.append(percentile)
        else:
            # radiant team
            radiant.append(float(MMR))
            radiant.append(percentile)

    if len(radiant) != 10 or len(dire) != 10:
        return (-1,-1)
    return (radiant + dire, y)

if __name__ == '__main__':
    # Parameters
    thr = 2;  # maximum tolerence threshold on the number of non-existent players in a match

    client = MongoClient()
    db = client['701']
    matches = db['matches']
    players = db['player']
    dist = db['distribution']
    x = []
    y = []

    MMR_dist = crawl_MMR_dist(dist)
    ids_MMRs = crawl_ids_MMRs(players)
    print str(len(ids_MMRs)) + ' players with account ids and MMRs'

    N = matches.count()
    print str(N) + ' matches found'

    bar = Bar('Extracting player-rank features in matches', max = N)
    for i, m in enumerate(matches.find()):
        bar.next()
        a,b = extract_player_rank(m, thr, ids_MMRs, MMR_dist)
        # print; print a
        # Skip those matches with too many non-existent players or that are not 5 vs 5
        if b == -1:
            continue
        x.append(a)
        y.append(b)
    bar.finish()

    X = np.array(x) # features
    Y = np.array(y) # label
    print 'Number of matches extracted: ' + str(X.shape[0])
    # Replace NaN with mean value
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)

    save_as_pk((X, Y), "player_rank_individual.pk")

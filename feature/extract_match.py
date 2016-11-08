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

def load_dict(filename):
    fin = open(filename, 'rb')
    return cPickle.load(fin)

# Format: [hero_id * 226, hero_attr * 260, hero_winrate * 25, player_mmrpec * 20, hero_player * 80] -> 611 dimensions
# Skip those matches that are not 5 vs 5, with hero_id = 0 , or with too many non-existent players
def extract_prior(m, thr, player_mmrpec):
    num_heros = 113  # according to hero_id.json, but "id": 24 is missing
    nonexistent_players = 0
    y = m['radiant_win']  # whether radiant won
    if len(m['players']) != 10:
        # print; print '< 10 players'
        return (-1, -1)

    # Save the hero ids and account ids for each team
    radiant_heros = []
    radiant_accts = []
    dire_heros = []
    dire_accts = []
    x = []
    for p in m['players']:
        # Skip matches with any hero_id is 0 (no attributes in database)
        hero_id = str(p['hero_id'])
        if hero_id == '0':
            # print; print 'invalid hero id'
            return (-1, -1)

        acct_id = str(p['account_id'])
        # Check for non-existent players: 4294967295 is a magic number according to data/info.txt
        if acct_id == '4294967295' or not player_mmrpec.has_key(acct_id):
            nonexistent_players += 1
            # Skip this match if non-existent players > threshold
            if nonexistent_players > thr:
                # print; print 'non-existent players > ' + str(thr)
                return (-1, -1)
            # Mark it as 'unknown_player' to look up in dictionaries
            acct_id = 'unknown_player'

        if p['player_slot'] < 5:
            # radiant team (slot 0 ~ 4)
            radiant_heros += [hero_id]
            radiant_accts += [acct_id]
        else:
            # dire team (slot 128 ~ 132)
            dire_heros += [hero_id]
            dire_accts += [acct_id]

    # print 'radiant_heros', radiant_heros
    # print 'radiant_accts', radiant_accts
    # print 'dire_heros', dire_heros
    # print 'dire_accts', dire_accts


    return (radiant_heros + dire_heros + radiant_accts + dire_accts+[y]+[m['duration'],m['match_id']], 1)

if __name__ == '__main__':
    # Parameters
    thr = 2   # maximum tolerance threshold on the number of non-existent players in a match
    client = MongoClient('yangyifans-MacBook-Pro.local')
    db = client['701']
    matches = db['matches']
    players = db['player']
    dist = db['distribution']
    x = []
    y = []
    N = matches.count()
    print str(N) + ' matches the dataset'

    # Load the .pk dictionaries
    print 'Loading dictionaries in .pk...'
    
    player_mmrpec = load_dict('player_mmrpec.pk')
    # Plug in average MMR and percentile calculated in avg_mmr_perc.py
    player_mmrpec['unknown_player'] = [4511.53467731, 0.87973183224]
    print 'Done!'

    bar = Bar('Extracting all prior features in matches', max = N)
    for i, m in enumerate(matches.find()):
        bar.next()
        a,b = extract_prior(m, thr, player_mmrpec)
        # print; print a
        # Skip those matches that are not 5 vs 5, with hero_id = 0, or with too many non-existent players    
        if b == -1:
            continue
        x.append(a)

    bar.finish()
    X = np.array(x) # features
    
    print 'Extracted ' + str(X.shape[0]) + ' valid matches, each with ' + str(X.shape[1]) + ' features'
    #radiant_heros + dire_heros + radiant_accts + dire_accts + [y]
    save_as_pk(X, "new_match.pk")

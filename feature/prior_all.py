import os, math
from pymongo import MongoClient
from progress.bar import Bar
#from progressbar import ProgressBar, Bar, Percentage, FormatLabel, ETA
from six.moves import cPickle
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import Imputer
from random import shuffle


def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()

def load_dict(filename):
    fin = open(filename, 'rb')
    return cPickle.load(fin)

# Format: [hero_id * 226, hero_attr * 260, hero_winrate * 25, player_mmrpec * 20, hero_player_attr * 70, hero_player_winrate * 10] -> 611 dimensions
# Skip those matches that are not 5 vs 5, with hero_id = 0 , or with too many non-existent players
def extract_prior(m, thr, player_mmrpec, hero_winrate, hero_attr, hero_player_attr, hero_player_winrate):
    num_heros = 113  # according to hero_id.json, but "id": 24 is missing
    nonexistent_players = 0
    # Save the hero ids and account ids for each team
    radiant_heros = m[:5]
    radiant_accts = m[10:15]
    dire_heros = m[5:10]
    dire_accts = m[15:20]
    if m[20]=='True':
        y =1
    elif m[20]=='False':
        y=0
    else:
        assert 1==0
    


    # print
    # print 'radiant_heros', radiant_heros
    # print 'radiant_accts', radiant_accts
    # print 'dire_heros', dire_heros
    # print 'dire_accts', dire_accts

    # [1] binary hero id: 113 * 2 = 226 dim
    f_hero_id = [0] * num_heros * 2
    # [2] hero attributes: 10 * 26 = 260 dim
    f_hero_attr = []
    # [3] hero_winrate: 5 * 5 = 25 dim
    f_hero_winrate = []
    # [4] player_mmrpec: 10 * 2 = 20 dim
    f_player_mmrpec = []
    # [5] hero_player_attr: 10 * 7 = 70 dim
    f_hero_player_attr = []
    # [6] hero_player_winrate: 10 * 7 = 10 dim
    f_hero_player_winrate = []

    # Loop through radiant team players
    for r in range(5):
        r_hero = radiant_heros[r]
        r_acct = radiant_accts[r]

        # Set to 1 at index 0 ~ 112
        f_hero_id[int(r_hero) - 1] = 1
        f_hero_attr += hero_attr[r_hero]
        f_player_mmrpec += player_mmrpec[r_acct]
        f_hero_player_attr += list(hero_player_attr[r_hero][r_acct])
        assert len(list(hero_player_attr[r_hero][r_acct]))==7
        f_hero_player_winrate += [hero_player_winrate[r_hero][r_acct]]
        # Loop through radiant-dire pairs
        for d in range(5):
            d_hero = dire_heros[d]
            f_hero_winrate += [hero_winrate[r_hero][d_hero]]
            
    # Loop through dire team players
    for d in range(5):
        d_hero = dire_heros[d]
        d_acct = dire_accts[d]

        # Set to 1 at index 113 ~ 225
        f_hero_id[int(d_hero) - 1 + num_heros] = 1
        f_hero_attr += hero_attr[d_hero]
        f_player_mmrpec += player_mmrpec[d_acct]

        f_hero_player_attr += list(hero_player_attr[d_hero][d_acct])
        assert len(list(hero_player_attr[d_hero][d_acct]))==7
        f_hero_player_winrate += [hero_player_winrate[d_hero][d_acct]]

    x = f_hero_id + f_hero_attr + f_hero_winrate + f_player_mmrpec + f_hero_player_attr + f_hero_player_winrate

    # print; print f_hero_player
    # print; print len(x)
    return (x, y)

if __name__ == '__main__':
    # Parameters
    thr = 2;  # maximum tolerance threshold on the number of non-existent players in a match
    matches = load_dict('new_match.pk')
    x = []
    y = []
    N = matches.shape[0]
    print str(N) + ' matches the dataset'

    # Load the .pk dictionaries
    print 'Loading dictionaries in .pk...'
    player_mmrpec = load_dict('player_mmrpec.pk')
    # Plug in average MMR and percentile calculated in avg_mmr_perc.py
    player_mmrpec['unknown_player'] = [4511.53467731, 0.897862092646]
    hero_winrate = load_dict('hero_winrate.pk')
    hero_attr = load_dict('hero_attr.pk')
    hero_player_attr = load_dict('hero_player_attr.pk')
    hero_player_winrate = load_dict('hero_player_winrate.pk')
    
    print 'Done!'
    D = []
    bar = Bar('Extracting all prior features in matches', max = N)
    for i, m in enumerate(matches):
        bar.next()
        a,b = extract_prior(m, thr, player_mmrpec, hero_winrate, hero_attr, hero_player_attr, hero_player_winrate)
        # print; print a
        # Skip those matches that are not 5 vs 5, with hero_id = 0, or with too many non-existent players
        minutes = float(m[-2])/60.
        if minutes<=20 or minutes>=60:
            continue
        if b == -1:
            continue

        x.append(a)
        y.append(b)        

        D.append(minutes)

    bar.finish()

    X = np.array(x, dtype='float32') # features
    Y = np.array(y, dtype='float32') # label
    D = np.array(D, dtype='float32') # label
    print 'Extracted ' + str(X.shape[0]) + ' valid matches, each with ' + str(X.shape[1]) + ' features'
    N = X.shape[0]
    assert X.shape[0]==Y.shape[0]
    idx = range(N)
    shuffle(idx)
    train_X = X[idx[:int(N*.9)]]
    train_Y = Y[idx[:int(N*.9)]]
    train_D = D[idx[:int(N*.9)]]
    test_X = X[idx[int(N*.9):]]
    test_Y = Y[idx[int(N*.9):]]
    test_D = D[idx[int(N*.9):]]
    save_as_pk((train_X, train_Y, train_D), "new_match_duration_train.pk")
    save_as_pk((test_X, test_Y, test_D), "new_match_duration_test.pk")

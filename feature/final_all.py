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

# Prior (611 dimensions): [hero_id * 226, hero_attr * 260, hero_winrate * 25, player_mmrpec * 20, hero_player_attr * 70, hero_player_winrate * 10]
# Online (22 * T dimensions): [XP * 10, gold * 10, kill * 2] * T
def extract_final(m, player_mmrpec, hero_winrate, hero_attr, hero_player_attr, hero_player_winrate):
    num_heros = 113  # according to hero_id.json, but "id": 24 is missing
    assert len(m['players']) == 10

    y = m['radiant_win']  # whether radiant won
    x = []

    # For prior features: Save the hero ids and account ids of each team for pickle lookups
    radiant_heros = []
    radiant_accts = []
    dire_heros = []
    dire_accts = []

    #####  Online features: combined in one variable for efficiency  ####
    # Calculate the exact dimension instead of list appends
    # T: number of minutes, +1 for the 0-th minute
    T = int(math.ceil(m['duration'] / 60.0)) + 1
    f_online = [0] * 22 * T

    for p in m['players']:
        # Skip the entire match if any player's any time series data do not exist
        if not p['xp_t']:
            # print; print "p['xp_t'] not exist"
            return (-1, -1)
        if not p['gold_t']:
            # print; print "p['gold_t'] not exist"
            return (-1, -1)

        hero_id = str(p['hero_id'])
        acct_id = str(p['account_id'])
        # Check for non-existent players: 4294967295 is a magic number according to data/info.txt
        if acct_id == '4294967295' or not player_mmrpec.has_key(acct_id):
            # Mark it as 'unknown_player' to look up in dictionaries
            acct_id = 'unknown_player'

        slot = p['player_slot']
        # xp_t: experience per minute
        xp_t = p['xp_t']
        # gold_t: gold per minute
        gold_t = p['gold_t']
        if slot < 5:
            # radiant team (slot 0 ~ 4)
            radiant_heros += [hero_id]
            radiant_accts += [acct_id]
            # online features
            for t in range(T):
                f_online[22 * t + slot] = xp_t[t]
                f_online[22 * t + 10 + slot] = gold_t[t]
        else:
            # dire team (slot 128 ~ 132)
            dire_heros += [hero_id]
            dire_accts += [acct_id]
            # online features
            for t in range(T):
                f_online[22 * t + slot - 123] = xp_t[t]
                f_online[22 * t + 10 + slot - 123] = gold_t[t]

    # print
    # print 'radiant_heros', radiant_heros
    # print 'radiant_accts', radiant_accts
    # print 'dire_heros', dire_heros
    # print 'dire_accts', dire_accts

    # Loop through team fights
    for tf in m['teamfights']:
        t = int(math.ceil(tf['last_death'] / 60.0))
        # array of each player's team fight contribution, indexed by their slot.
        tf_p = tf['players']
        for r in range(0,5):
            # Aggregate death counts for t-th minute and beyond
            for minute in range(t,T):
                f_online[22 * minute + 20] += tf_p[r]['deaths']
        for d in range(5,10):
            for minute in range(t,T):
                f_online[22 * minute + 21] += tf_p[d]['deaths']

    ####  Prior features  ####
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

    # Aggregate prior features
    x += f_hero_id + f_hero_attr + f_hero_winrate + f_player_mmrpec + f_hero_player_attr + f_hero_player_winrate
    # print; print x
    # print; print f_online
    x += f_online

    # print; print f_hero_player
    # print; print len(x)
    # raw_input()
    return (x, y)

if __name__ == '__main__':
    # Parameters
    # thr = 2;  # maximum tolerance threshold on the number of non-existent players in a match
    # matches = load_dict('new_match.pk')
    client = MongoClient()
    db = client['701']
    matches = db['realtime']
    X = []
    y = []
    N = matches.count()
    print str(N) + ' matches in the dataset'

    # Load the .pk dictionaries
    print 'Loading dictionaries in .pk...'
    print 'player_mmrpec.pk'
    player_mmrpec = load_dict('player_mmrpec.pk')
    # Plug in average MMR and percentile calculated in avg_mmr_perc.py
    player_mmrpec['unknown_player'] = [4511.53467731, 0.897862092646]
    print 'hero_winrate.pk'
    hero_winrate = load_dict('hero_winrate.pk')
    print 'hero_attr.pk'
    hero_attr = load_dict('hero_attr.pk')
    print 'hero_player_attr.pk'
    hero_player_attr = load_dict('hero_player_attr.pk')
    print 'hero_player_winrate.pk'
    hero_player_winrate = load_dict('hero_player_winrate.pk')
    print 'Done!'

    # D = []
    bar = Bar('Extracting all final (prior + online) features in matches', max = N)
    for m in matches.find():
        bar.next()
        a,b = extract_final(m, player_mmrpec, hero_winrate, hero_attr, hero_player_attr, hero_player_winrate)
        if b == -1:
            continue
        # print; print a
        # Skip those matches that are not 5 vs 5, with hero_id = 0, or with too many non-existent players
        # minutes = float(m[-2])/60.
        # if minutes<=20 or minutes>=60:
        #     continue

        # Numpy cannot handle matrices with variable-length rows, so we use
        # a "list of numpy vectors" for X instead
        X.append(np.array(a, dtype = 'float32'))
        y.append(b)

        # D.append(minutes)

    bar.finish()

    # X = np.array(x, dtype='float32') # features
    Y = np.array(y, dtype='int') # label
    # D = np.array(D, dtype='float32') # label
    print 'Extracted ' + str(len(X)) + ' valid matches, each with variable-length features'
    save_as_pk((X, Y), "final_all.pk")


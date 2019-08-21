import os
from pymongo import MongoClient
from progress.bar import Bar
from six.moves import cPickle
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import Imputer
import math

num_heroes = 113

def load_pk(filename):
    fin = open(filename,"rb")
    return cPickle.load(fin)

def save_as_pk(data,filename):
	fout = open(filename,'wb')
	cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
	fout.close()

"""
hero_player_winrate = load_pk("hero_player_winrate.pk")
hero_player_attr = load_pk("hero_player_attr.pk")

hero_player = {}
for hero_id in range(1, num_heroes+1):
	hero_player[str(hero_id)] = {}

key_error = 0
for hero_id in hero_player_attr.keys():
	for player_id in hero_player_attr[hero_id].keys():
		try:
			hero_player[hero_id][player_id] = list(np.append(hero_player_winrate[hero_id][player_id], hero_player_attr[hero_id][player_id]))
		except KeyError:
			print 'key error' + str(key_error) + '...'
			key_error += 1
			continue
"""
hero_player = load_pk("hero_player.pk")
print hero_player['1']['unknown_player']
#save_as_pk(hero_player, "hero_player.pk")
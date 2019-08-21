from pymongo import MongoClient
import numpy as np
from six.moves import cPickle
from progress.bar import Bar

num_heroes = 113

def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()

if __name__ == '__main__':
	client = MongoClient() 
	db = client['701']
	matches = db['matches']
	N = matches.count()
	print "%d matches found in total" % N

	winrate = {}										# hero vs hero winning rate
	for i in range(1, num_heroes+1):
		winrate[str(i)] = {}
		for j in range(1, num_heroes+1):
			winrate[str(i)][str(j)] = 0.0

	bar = Bar('Processing', max=N)
	for i, m in enumerate(matches.find()):				# going through all matches to calculate winrate
		bar.next()
		radiant_win = m['radiant_win'] 					# whether radiant won
		radiant = []
		dire = []
		for p in m['players']:
			if p['hero_id'] != 0:						# hero_id = 0 means this player quited
				if p['player_slot'] >= 128: 			# dire team
					dire.append(str(p['hero_id']))
				else:
					radiant.append(str(p['hero_id'])) 	# radiant team

		for rhero in radiant:
			for dhero in dire:
				if radiant_win:
					winrate[rhero][dhero] += 1.0
				else:
					winrate[dhero][rhero] += 1.0
	bar.finish()

	for i in range(1, num_heroes+1):
		for j in range(i, num_heroes+1):
			total_cnt = winrate[str(i)][str(j)] + winrate[str(j)][str(i)]
			if total_cnt != 0:
				winrate[str(i)][str(j)] = winrate[str(i)][str(j)] / total_cnt
				if str(i) != j:
					winrate[str(j)][str(i)] = winrate[str(j)][str(i)] / total_cnt
			else:
				winrate[str(i)][str(j)] = 0.5
				winrate[str(j)][str(i)] = 0.5

	print winrate

	save_as_pk(winrate, 'hero_winrate.pk')

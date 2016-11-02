import os
from pymongo import MongoClient
from progress.bar import Bar
from six.moves import cPickle
import numpy as np
from sklearn import preprocessing

num_heroes = 113
percentile = [{"bin":0,"bin_name":0,"count":1930,"cumulative_sum":1930},{"bin":1,"bin_name":100,"count":1056,"cumulative_sum":2986},{"bin":2,"bin_name":200,"count":1428,"cumulative_sum":4414},{"bin":3,"bin_name":300,"count":1979,"cumulative_sum":6393},{"bin":4,"bin_name":400,"count":2593,"cumulative_sum":8986},{"bin":5,"bin_name":500,"count":3254,"cumulative_sum":12240},{"bin":6,"bin_name":600,"count":4088,"cumulative_sum":16328},{"bin":7,"bin_name":700,"count":4943,"cumulative_sum":21271},{"bin":8,"bin_name":800,"count":5833,"cumulative_sum":27104},{"bin":9,"bin_name":900,"count":7279,"cumulative_sum":34383},{"bin":10,"bin_name":1000,"count":9747,"cumulative_sum":44130},{"bin":11,"bin_name":1100,"count":10601,"cumulative_sum":54731},{"bin":12,"bin_name":1200,"count":11649,"cumulative_sum":66380},{"bin":13,"bin_name":1300,"count":13209,"cumulative_sum":79589},{"bin":14,"bin_name":1400,"count":14735,"cumulative_sum":94324},{"bin":15,"bin_name":1500,"count":15984,"cumulative_sum":110308},{"bin":16,"bin_name":1600,"count":17603,"cumulative_sum":127911},{"bin":17,"bin_name":1700,"count":19309,"cumulative_sum":147220},{"bin":18,"bin_name":1800,"count":21450,"cumulative_sum":168670},{"bin":19,"bin_name":1900,"count":24846,"cumulative_sum":193516},{"bin":20,"bin_name":2000,"count":32200,"cumulative_sum":225716},{"bin":21,"bin_name":2100,"count":32477,"cumulative_sum":258193},{"bin":22,"bin_name":2200,"count":34857,"cumulative_sum":293050},{"bin":23,"bin_name":2300,"count":37458,"cumulative_sum":330508},{"bin":24,"bin_name":2400,"count":41036,"cumulative_sum":371544},{"bin":25,"bin_name":2500,"count":44001,"cumulative_sum":415545},{"bin":26,"bin_name":2600,"count":46308,"cumulative_sum":461853},{"bin":27,"bin_name":2700,"count":48963,"cumulative_sum":510816},{"bin":28,"bin_name":2800,"count":51463,"cumulative_sum":562279},{"bin":29,"bin_name":2900,"count":56998,"cumulative_sum":619277},{"bin":30,"bin_name":3000,"count":76756,"cumulative_sum":696033},{"bin":31,"bin_name":3100,"count":68862,"cumulative_sum":764895},{"bin":32,"bin_name":3200,"count":66535,"cumulative_sum":831430},{"bin":33,"bin_name":3300,"count":64136,"cumulative_sum":895566},{"bin":34,"bin_name":3400,"count":63104,"cumulative_sum":958670},{"bin":35,"bin_name":3500,"count":61504,"cumulative_sum":1020174},{"bin":36,"bin_name":3600,"count":56197,"cumulative_sum":1076371},{"bin":37,"bin_name":3700,"count":52467,"cumulative_sum":1128838},{"bin":38,"bin_name":3800,"count":48706,"cumulative_sum":1177544},{"bin":39,"bin_name":3900,"count":45492,"cumulative_sum":1223036},{"bin":40,"bin_name":4000,"count":66039,"cumulative_sum":1289075},{"bin":41,"bin_name":4100,"count":45452,"cumulative_sum":1334527},{"bin":42,"bin_name":4200,"count":38560,"cumulative_sum":1373087},{"bin":43,"bin_name":4300,"count":32551,"cumulative_sum":1405638},{"bin":44,"bin_name":4400,"count":27884,"cumulative_sum":1433522},{"bin":45,"bin_name":4500,"count":23902,"cumulative_sum":1457424},{"bin":46,"bin_name":4600,"count":17630,"cumulative_sum":1475054},{"bin":47,"bin_name":4700,"count":12967,"cumulative_sum":1488021},{"bin":48,"bin_name":4800,"count":9511,"cumulative_sum":1497532},{"bin":49,"bin_name":4900,"count":7448,"cumulative_sum":1504980},{"bin":50,"bin_name":5000,"count":13313,"cumulative_sum":1518293},{"bin":51,"bin_name":5100,"count":5837,"cumulative_sum":1524130},{"bin":52,"bin_name":5200,"count":4013,"cumulative_sum":1528143},{"bin":53,"bin_name":5300,"count":2889,"cumulative_sum":1531032},{"bin":54,"bin_name":5400,"count":2283,"cumulative_sum":1533315},{"bin":55,"bin_name":5500,"count":1906,"cumulative_sum":1535221},{"bin":56,"bin_name":5600,"count":1247,"cumulative_sum":1536468},{"bin":57,"bin_name":5700,"count":935,"cumulative_sum":1537403},{"bin":58,"bin_name":5800,"count":766,"cumulative_sum":1538169},{"bin":59,"bin_name":5900,"count":558,"cumulative_sum":1538727},{"bin":60,"bin_name":6000,"count":1316,"cumulative_sum":1540043},{"bin":61,"bin_name":6100,"count":520,"cumulative_sum":1540563},{"bin":62,"bin_name":6200,"count":378,"cumulative_sum":1540941},{"bin":63,"bin_name":6300,"count":261,"cumulative_sum":1541202},{"bin":64,"bin_name":6400,"count":213,"cumulative_sum":1541415},{"bin":65,"bin_name":6500,"count":224,"cumulative_sum":1541639},{"bin":66,"bin_name":6600,"count":146,"cumulative_sum":1541785},{"bin":67,"bin_name":6700,"count":134,"cumulative_sum":1541919},{"bin":68,"bin_name":6800,"count":90,"cumulative_sum":1542009},{"bin":69,"bin_name":6900,"count":97,"cumulative_sum":1542106},{"bin":70,"bin_name":7000,"count":173,"cumulative_sum":1542279},{"bin":71,"bin_name":7100,"count":89,"cumulative_sum":1542368},{"bin":72,"bin_name":7200,"count":57,"cumulative_sum":1542425},{"bin":73,"bin_name":7300,"count":43,"cumulative_sum":1542468},{"bin":74,"bin_name":7400,"count":41,"cumulative_sum":1542509},{"bin":75,"bin_name":7500,"count":42,"cumulative_sum":1542551},{"bin":76,"bin_name":7600,"count":23,"cumulative_sum":1542574},{"bin":77,"bin_name":7700,"count":21,"cumulative_sum":1542595},{"bin":78,"bin_name":7800,"count":5,"cumulative_sum":1542600},{"bin":79,"bin_name":7900,"count":11,"cumulative_sum":1542611},{"bin":80,"bin_name":8000,"count":19,"cumulative_sum":1542630},{"bin":81,"bin_name":8100,"count":10,"cumulative_sum":1542640},{"bin":82,"bin_name":8200,"count":6,"cumulative_sum":1542646},{"bin":83,"bin_name":8300,"count":3,"cumulative_sum":1542649},{"bin":84,"bin_name":8400,"count":3,"cumulative_sum":1542652},{"bin":85,"bin_name":8500,"count":3,"cumulative_sum":1542655},{"bin":87,"bin_name":8700,"count":3,"cumulative_sum":1542658},{"bin":88,"bin_name":8800,"count":1,"cumulative_sum":1542659},{"bin":89,"bin_name":8900,"count":1,"cumulative_sum":1542660},{"bin":91,"bin_name":9100,"count":1,"cumulative_sum":1542661}]

def save_as_pk(data,filename):
	fout = open(filename,'wb')
	cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
	fout.close()

if __name__ == '__main__':
	client = MongoClient() 
	db = client['701']
	player = db['player']
	N = player.count()
	print 'Scanning through ' + str(N) + ' players in collection "player"...'

	hero_player_winrate = {}
	for hero_id in range(1, num_heroes+1):
		hero_player_winrate[str(hero_id)] = {}


	for i, m in enumerate(player.find()):
		player_id = str(m['account_id'])
		for hero in m['heroes']:
			if hero['games'] > 10:
				hero_player_winrate[hero['hero_id']][player_id] = float(hero['win']) / hero['games']
			else:
				hero_player_winrate[hero['hero_id']][player_id] = 0.5

	hero_avg_winrate = {}
	for hero_id in range(1, num_heroes+1):
		hero_avg_winrate[str(hero_id)] = 0.0
	for hero_id in hero_player_winrate.keys():
		for player_id in hero_player_winrate[hero_id].keys():
			hero_avg_winrate[hero_id] += hero_player_winrate[hero_id][player_id]
	for hero_id in range(1, num_heroes+1):
		hero_avg_winrate[str(hero_id)] /= N

	for hero_id in range(1, num_heroes+1):
		hero_player_winrate[str(hero_id)]['unknown_player'] = hero_avg_winrate[str(hero_id)]

	print hero_player_winrate['1']
	save_as_pk(hero_player_winrate, 'hero_player_winrate.pk')
	

	"""
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
	"""
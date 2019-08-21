from pymongo import MongoClient
import numpy as np
from six.moves import cPickle
from progress.bar import Bar

num_heroes = 113

def save_as_pk(data,filename):
    fout = open(filename,'wb')
    cPickle.dump(data,fout,protocol=cPickle.HIGHEST_PROTOCOL)
    fout.close()

def load_pk(filename):
    fin = open(filename,"rb")
    return cPickle.load(fin)

if __name__ == '__main__':
	client = MongoClient() 
	db = client['701']
	hero = db['hero']

	hero_attr = {}

	for i, hero_info in enumerate(hero.find()):
		id = str(hero_info['ID'])
		hero_info.pop('Name')
		hero_info.pop('Patch')
		hero_info.pop('ID')
		hero_info.pop('_id')
		hero_info.pop('Alignment')
		hero_attr[id] = hero_info.values()
		#print hero_info.keys()

	print hero_attr.keys()
	save_as_pk(hero_attr, 'hero_attr.pk')
	


import os
from pymongo import MongoClient
from progress.bar import Bar
#from progressbar import ProgressBar, Bar, Percentage, FormatLabel, ETA

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

def get_nonexistent_players(m, account_ids):
    nonexistent_players = 0
    for p in m['players']:
        # non-existent player: invalid account_id or not in player collection
        account_id = p['account_id']
        if account_id == 4294967295: # magic number according to data/info.txt
            # print; print 'invalid account id'
            nonexistent_players += 1
        elif account_id not in account_ids:
            # print; print 'account id not in player collection'
            nonexistent_players += 1
    return nonexistent_players

if __name__ == '__main__':
    client = MongoClient() 
    db = client['701']
    matches = db['matches']
    N = matches.count()

    account_ids = crawl_account_ids(db['player'])

    print 'Number of matches: ', N
    hist = [0] * 11 # histogram of non-existent players
    bar = Bar('Counting non-existent players in matches', max = N)
    for i, m in enumerate(matches.find()):
        bar.next()
        non = get_nonexistent_players(m, account_ids)
        # print; print non
        hist[non] += 1
    bar.finish()

    # Write the histogram to a file
    file = open('hist_nonexistent_players.txt', 'w')
    print 'Number of matches: ' + str(N)
    file.write('Number of matches: ' + str(N) + '\n')
    print 'Histogram of non-existent players (invalid account ids or not in player collection)'
    file.write('Histogram of non-existent players (invalid account ids or not in player collection)\n')
    for i, count in enumerate(hist):
        print str(i) + ': ' + str(count)
        file.write(str(i) + ': ' + str(count) + '\n')


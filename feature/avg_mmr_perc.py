import os, math
from pymongo import MongoClient
from progress.bar import Bar

def crawl_MMR_dist(dist):
    MMR_dist = [0] # 0-th element: number of players below those with MMR 0~99 = 0
    for bin in dist.find():
        MMR_dist.append(bin['cumulative_sum'])
    return MMR_dist

if __name__ == '__main__':
    client = MongoClient()
    db = client['701']
    players = db['player']
    dist = db['distribution']

    MMR_dist = crawl_MMR_dist(dist)
    total_players = MMR_dist[-1]

    cnt = 0
    sum_MMR = 0.0
    sum_perc = 0.0
    bar = Bar('Calculating average MMR and percentile', max = players.count())
    # Skip those players without a profile to prevent errors
    for p in players.find({'profile': {'$exists': True}}):
        bar.next()
        cnt += 1
        MMR = p['mmr_estimate']['estimate']
        sum_MMR += MMR
        perc = float(MMR_dist[MMR // 100]) / float(total_players)  # based on Solo MMR
        # print; print perc
        sum_perc += perc

    bar.finish()

    avg_MMR = sum_MMR / float(cnt)
    avg_perc = sum_perc / float(cnt)
    print 'Avaerage MMR: ' + str(avg_MMR) + ', Average percentile: ' + str(avg_perc)


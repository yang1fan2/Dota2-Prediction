from pymongo import MongoClient
from progress.bar import Bar
from six.moves import cPickle
import numpy as np
from matplotlib import pyplot as plt


def load_dict(filename):
    fin = open(filename, 'rb')
    return cPickle.load(fin)

def crawl_acct_ids(players):
    # Append account ids in a list
    ids = []
    bar = Bar('Crawling account ids', max = players.count())
    # Skip those players without profiles to prevent errors
    for p in players.find({'profile': {'$exists': True}}):
        bar.next()
        acct_id = p['account_id']
        # print; print acct_id
        if acct_id != 4294967295:
            ids.append(str(acct_id))
    bar.finish()
    return ids

def barplot(p1, p2, mat, fig):
    plot_X = np.arange(10)
    # [player 1 top 5 (descending), player 2 top 5 (descending]
    hero_sel1 = np.argsort(mat[p1,:])[-1:-6:-1]
    hero_sel2 = np.argsort(mat[p2,:])[-1:-6:-1]
    if fig == 2:
        # [player 1 top (5,2,1,3,4), player 2 top (5,2,1,3,4)]
        hero_sel1 = hero_sel1[[4,1,0,2,3]]
        hero_sel2 = hero_sel2[[4,1,0,2,3]]

    plot_Y1 = mat[p1, np.hstack((hero_sel1, hero_sel2))]
    plot_Y2 = mat[p2, np.hstack((hero_sel1, hero_sel2))]
    print plot_Y1
    print plot_Y2
    plt.close(fig)
    plt.figure(fig)
    plt.bar(np.arange(len(plot_X)), +plot_Y1, facecolor='#9999ff', edgecolor='white')
    plt.bar(np.arange(len(plot_X)), -plot_Y2, facecolor='#ff9999', edgecolor='white')
    for x, y in zip(plot_X, plot_Y1):
        plt.text(x + 0.4, y + 0.05, '%.2f' % y, ha='center', va='bottom', fontsize=16)

    for x, y in zip(plot_X, plot_Y2):
        plt.text(x + 0.4, -y - 0.05, '%.2f' % y, ha='center', va='top', fontsize=16)

    plt.xlim(-.5, len(plot_X))
    plt.xticks(())
    plt.ylim(-1.2, +1.2)
    plt.yticks(())
    plt.show()


if __name__ == '__main__':
    num_heros = 113
    client = MongoClient()
    db = client['701']
    players = db['player']

    print 'Loading hero_player_winrate...'
    # winrate['hero_id']['account_id'] = a float between 0-1
    winrate = load_dict('hero_player_winrate.pk')
    print 'Done!'

    print 'Crawling player account ids...'
    ids = crawl_acct_ids(players)
    print 'Done!'

    # Filter players
    cnt_players = 0
    mat = []
    acct = []
    for p in ids:
        # default winrate = 0.5 in .pk
        p_rates = [0.5] * (num_heros + 1)
        for hero in range(1,num_heros+1):
            # hero id 24 is missing in the database
            if hero == 24:
                continue
            rate = winrate[str(hero)][p]
            # print 'account: ' + p + ', hero: ' + str(hero) + ', winrate: ' + str(rate)
            p_rates[hero] = (rate)
        p_rates = np.array(p_rates)
        # Thresholds: Large enough Number of used hero ids, large enough std
        thr_used_heros = 50;
        num_used_heros = sum(p_rates != 0.5)
        thr_std = 0.12
        if num_used_heros >= thr_used_heros and np.std(p_rates) >= thr_std:
            cnt_players += 1
            print 'account:' + p + ', min: ' + str(np.min(p_rates)) \
            + ' (' + str(np.argmin(p_rates)) + '), max: ' + str(np.max(p_rates)) \
            + ' (' + str(np.argmax(p_rates)) + '), std: ' + str(np.std(p_rates)) \
            + ', # used heros: ' + str(num_used_heros)
            mat.append(p_rates)
            acct.append(p)
    mat = np.array(mat)
    print cnt_players, 'players'
    # # Plot a heat map
    # fig, ax = ppl.subplots(1)
    # ppl.pcolormesh(fig, ax, mat)

    # Calculate and sort pair-wise L1 distance
    # dist = distance.squareform(distance.pdist(mat, 'cityblock'))
    # # Found player 0 vs. player 42
    # plot_X = np.arange(num_heros+1)
    # # hero_sel = np.bitwise_and(player1 != 0.5, player2 != 0.5)
    # hero_sel = [1,4,6,7,8,11,12,15,16,17]
    # plot_Y1 = mat[0,hero_sel]
    # plot_Y2 = mat[42,hero_sel]
    # plt.figure()
    # plt.bar(np.arange(len(hero_sel)), +plot_Y1, facecolor='#9999ff', edgecolor='white')
    # plt.bar(np.arange(len(hero_sel)), -plot_Y2, facecolor='#ff9999', edgecolor='white')
    # for x, y in zip(plot_X, plot_Y1):
    #     plt.text(x + 0.4, y + 0.05, '%.2f' % y, ha='center', va='bottom')
    #
    # for x, y in zip(plot_X, plot_Y2):
    #     plt.text(x + 0.4, -y - 0.05, '%.2f' % y, ha='center', va='top')
    #
    # plt.xlim(-.5, len(hero_sel))
    # plt.xticks(())
    # plt.ylim(-1.0, +1.0)
    # plt.yticks(())
    # plt.show()

    for p in range(mat.shape[0]):
        top_heros = np.argsort(mat[p,:])[-1:-6:-1]
        print 'player ' + str(p) + ' (' + acct[p] + '): top 5 heros = ' + str(top_heros) + ', winrates = ' + str(mat[p,top_heros])

    # Determine 2 players to plot
    p1 = 9
    p2 = 10

    # [player 1 top 5 (descending), player 2 top 5 (descending]
    barplot(p1, p2, mat, 1)
    # [player 1 top (5,2,1,3,4), player 2 top (5,2,1,3,4)]
    barplot(p1, p2, mat, 2)

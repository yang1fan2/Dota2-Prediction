#https://wiki.teamfortress.com/wiki/WebAPI/GetMatchHistory
import json
import dota2api
import cPickle
import time
#start steamids=111114687
#match_id= 2130193456 : start_time 2016/2/5 10:17:29
# 4294967295: private account
player_counter =  {}
player_done = {111114687:1}
match_done = {}
Q = [111114687]
start = 0
end = 0
result=[]
max_iter = 10
store_matches = 100000

def get_by_account_id():
    global start,end
    idx = Q[start]
    print idx,player_counter.get(idx,0)
    start+=1    
    while True:
        try:
            response = api.get_match_history(skill=3,matches_requested=500,
                    account_id=idx,min_player=10,game_mode=2)
        except Exception,e:
            print 'calling api failed '+str(e)

#            time.sleep(1)
            break
        if response['status'] == 1:
            if len(response['matches'])==0:
                print 'response is empty'
                break
            for m in response['matches']:
                if not m['match_id'] in match_done:
                    match_done[m['match_id']] = 1
                    try:
                        for p in m['players']:
                            player_counter[p['account_id']] = player_counter.get(p['account_id'],0) + 1
                            if not p['account_id'] in player_done:
                                end+=1
                                Q.append(p['account_id'])
                                player_done[p['account_id']] = 1
                                if player_counter[Q[end]]>player_counter[Q[start]]:
                                    Q[start], Q[end] = Q[end], Q[start]
                        result.append(m)
                    except:
                        print 'retrieving match detail failed'
                        continue
            break

        else:
            print response['statusDetail']        

def store(filename):
    fout = open(filename,"w")
    fout.write("number of matches %d\n"%len(match_done))
    fout.write("number of players %d\n"%len(player_counter))
    d = player_counter.items()
    d.sort(key= lambda x:-x[1])
    for k,v in d:
        fout.write("%d %d\n"%(k,v))
    fout.close()

if __name__ == '__main__':
    api = dota2api.Initialise("A0D097C39AFDA60C0A0B5F95DE85D348")
    current = 0

    while (start<=end) and (current < max_iter):
        print start,end
        get_by_account_id()
        if len(result) >= store_matches:
            print 'saving'
            f = open("very_high/%d(%d).pk"%(current,len(result)),"wb")
            cPickle.dump(result,f,protocol=cPickle.HIGHEST_PROTOCOL)
            result[:] = []
            current += 1
            f.close()
            store('info.txt')

    


    #response = api.get_match_details(match_id=2130193456)
    #response = api.get_match_history(account_id=111114687,
     #           matches_requested=100,skill=3,min_players=10)
    # response = api.get_match_history(skill=3,
    #     start_match_id=2667916950,
    #     matches_requested=101,
    #     account_id=111114687,
    #     min_player=10)
    #date_min=1475367354)#2016/01/08
    #print api.get_player_summaries(steamids=111114687)
    #print len(get_by_account_id(111114687))
    
    # print response['num_results']
    # print response['total_results']
    # print response['results_remaining']
    #print sum([1 for e in response['matches'] for i in e['players']if i['account_id']==24848117])
    #print '2697788116'
    #print min([e['match_id']for e in response['matches']]),max([e['match_id']for e in response['matches']])
    
    #print [e['match_id']for e in response['matches']]
    #print response['matches'][-1]['start_time']
    #print response
    #print response['num_results']
    #print len(response['matches'])
    '''
    start_match_id = 2130193456
    max_matches_num = 200
    matches = []
    max_requests = 10000
    now = 0
    store_every_matches = 10000
    cnt = 0
    while now < max_requests:
        try:
            response = api.get_match_history(start_at_match_id=start_match_id,
                matches_requested=max_matches_num,skill=3,min_players=10)
        except:
            time.sleep(2)
            continue
        print now
        if response['status'] == 1:
            response = dict(response)
            matches += response['matches']
            now += 1
            start_match_id =min([e['match_id']for e in response['matches']]) -1
            #print [e['match_id']for e in response['matches']]
            print start_match_id
        else:
            print response['statusDetail']
        if len(matches)% store_every_matches ==0:
            f = open("very_high/%d(%d).pk"%(cnt,start_seq_num-1),"wb")
            #id_(last_seq_num).pk
            cPickle.dump(matches,f,protocol=cPickle.HIGHEST_PROTOCOL)
            matches[:] = []
            cnt+=1
            f.close()

    
    
'''
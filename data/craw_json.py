import json
import dota2api
import cPickle
import time
#seq_num= 2250193456 : start_time 2016/8/16 14:2:47
if __name__ == '__main__':
    api = dota2api.Initialise("A0D097C39AFDA60C0A0B5F95DE85D348")

    start_seq_num = 2250193456
    max_matches_num = 100
    matches = []
    max_requests = 10000
    now = 0
    store_every_matches = 10000
    cnt = 0
    while now < max_requests:
        try:
            response = api.get_match_history_by_seq_num(start_at_match_seq_num=start_seq_num,
                matches_requested=max_matches_num)
        except:
            time.sleep(2)
            continue
        print now
        if response['status'] == 1:
            response = dict(response)
            matches += response['matches']
            now += 1
            start_seq_num =max([e['match_seq_num']for e in response['matches']]) +1
            print start_seq_num
        else:
            print response['statusDetail']
        if len(matches)% store_every_matches ==0:
            f = open("matches/%d(%d).pk"%(cnt,start_seq_num-1),"wb")
            #id_(last_seq_num).pk
            cPickle.dump(matches,f,protocol=cPickle.HIGHEST_PROTOCOL)
            matches = []
            cnt+=1
            f.close()

    
    


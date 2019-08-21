from pymongo import MongoClient
import os,time
from six.moves import cPickle
import numpy as np

client = MongoClient('localhost', 27017)
db = client['701']
match_collection = db.matches

if __name__ == '__main__':
    most_recent_match_id = 0
    for post in match_collection.find({}).sort('_id', direction=-1).limit(1):
        most_recent_match_id = post['match_id']
        most_recent_match_time = post['start_time']
    for post in match_collection.find({}).sort('_id', direction=1).limit(1):
        most_early_match_time =  post['start_time']
    total_matches = match_collection.count()
    recent_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(most_recent_match_time))
    early_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(most_early_match_time))
    disk_stats = os.statvfs('/')
    mb_remaining = disk_stats.f_bavail * disk_stats.f_frsize/1024.0/1024.0/1024.0
    duration = match_collection.aggregate([{"$avg": "$duration"}])
    print duration
    msg = '''

    Hello! 
    The database currently contains %s matches.
    The most recent match_id added to the database was %s.
    The date of that match was %s.
    The earliest match was %s.
    There are %.2f remaining GB on the hard drive.
    <3 dotabot
    ''' % (total_matches, most_recent_match_id, recent_time, early_time, mb_remaining) 
    print msg   
#!/usr/bin/python

import sys
import json
import time
import tweepy
import textwrap
import datetime
from srt import config
from srt.encoding import str_to_code, code_to_str

def load_data(path):
    with open(path) as f:
        json_list = f.readlines()
    data={}
    for i, j in enumerate(json_list):
        tweet=json.loads(j)
        seq = int(tweet["date"]) % config.NUM_MESSAGES
        data[seq] = tweet["id"]
    return data

def hide(path, data):
    tw = textwrap.wrap(path, config.CHARS_X_INTERACTION, \
                       drop_whitespace=False)
    interactions = []
    for mm in tw:
        base, offset = str_to_code(mm)
        if offset==0:
            interactions.append(str(data[base])+':R')
        elif offset==1:
            interactions.append(str(data[base])+':L')
        else:
            interactions.append(str(data[base])+':RL')

    return ','.join(interactions)


def unhide(path):
    interactions = path.split(",")
    message=''
    for r in interactions:
        base, actions = r.split(':')
        base = int(base)
        print "|", base, "|"
        offset = 0
        if 'L' in actions:
            offset = 1
        if 'RL' in actions:
            offset = 2

        message += code_to_str(base, offset)
    return message


def send_message(id_string):
    print "ID string:", id_string

    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(config.TWITTER_KEY, config.TWITTER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    interactions = id_string.split(",")
    for r in interactions:
        tid, actions = r.split(':')
        if 'RL' in actions:
            print "Retweet & Like:", tid
            api.retweet(tid)
            api.create_favorite(tid)
        elif 'L' in actions:
            print "Like:", tid
            api.create_favorite(tid)
        else:
            print "Retweet:", tid
            api.retweet(tid)

def read_message(screen_name):

    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(config.TWITTER_KEY, config.TWITTER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    interactions = ""
    tweets = api.user_timeline(screen_name, count=10)
    for t in reversed(tweets):
        ts = int(time.mktime(t.retweeted_status.created_at.timetuple())) + 3600*2
        seq = ts % config.NUM_MESSAGES
        print t.id, ts, t.retweeted_status.created_at, t.text
        #print json.dumps(t._json, indent=2)
        interactions += str(seq)
        if t.favorited:
            interactions += ":L"
        elif t.retweeted:
            interactions += ":R"
        else:
            interactions += ":RL"   

        interactions += ','

    return interactions[:-1]


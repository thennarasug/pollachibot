# Twython twitter api
import time


import glob
import os
import sqlite3
import traceback
import pandas as pd

# TelegramBot
import telepot

from twython import Twython, TwythonError
#heroku env variables
from os import environ

import time

def create_table():
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS pollachi (id string primary key)")
    try:
        db.commit()
    except:
        db.rollback()


def insert_error_string(id):
    c = db.cursor()
    try:
        vals = [id]
        query = "INSERT INTO pollachi (id) VALUES (?)"
        c.execute(query, vals)
        db.commit()
    except sqlite3.IntegrityError as i:
        pass
    except:
        error = traceback.print_exc()
        db.rollback()


def select_error_string(id):
    try:
        query = "select count(*) from pollachi where id = '{}'".format(id)
        #data = pd.read_sql(query, con=db)
        cursor = db.execute(query)
        db.commit()
        return cursor
    except:
        error = traceback.print_exc()
        db.rollback()
        return None

# for database
dbfilewithpath = ".\\pollachi.db"
db = sqlite3.connect(dbfilewithpath)
create_table()

keywords =  ['pollachi','பொள்ளாச்சி']

APP_KEY = environ.get('APP_KEY')
APP_SECRET = environ.get('APP_SECRET')
OAUTH_TOKEN = environ.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = environ.get('OAUTH_TOKEN_SECRET')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#indefinite while loop that runs every 1 hour. To remove the dependency on scheduler.
while True:
    count=0
    trycount=0
    totalcount=0
    for keyword in keywords:
        for lang_list in ['en','ta']:
            for result_type in ['popular','mixed', 'recent']:
                try:
                    #count=100 max (default 15), result_type='mixed' or 'recent'
                    #count=15 max (default 15), result_type='popular'
                    search_results = twitter.search(q=keyword,count=100, lang=lang_list, result_type=result_type)
                except TwythonError as e:
                    print(e)

                 # print(search_results)
                if len(search_results) > 0:
                    for tweet in search_results['statuses']:
                        utf8Pollachi = keyword.lower().encode('utf-8')
                        totalcount = totalcount + 1
                        #"RT @" not in tweet['text'] and
                        if  "pollachibot" != tweet['user']['screen_name'] and utf8Pollachi in tweet['text'].lower().encode('utf-8') and tweet['user']['screen_name'] not in ['SIGNAL_POLLACHI']:
                            try:
                                cursor = select_error_string(tweet['id'])
                                for row in cursor:
                                    if row[0] == 0:
                                        trycount = trycount + 1
                                        twitter.retweet(id=int(tweet['id']))
                                        count = count + 1
                                        print(tweet['user']['screen_name'], "-->", tweet['id'], "--->", keyword.lower(), "--->",
                                              tweet['text'].lower())
                                        insert_error_string(tweet['id'])

                            except TwythonError as e:
                                if "You have already retweeted this Tweet" in str(e):
                                    insert_error_string(tweet['id'])
                                print(e)

                    print(keyword, " in ", lang_list, ". Total filtered and retweeted ---> ", str(count), " / ", str(trycount),
                          " / ", str(totalcount))
    print("end of search")
    print("sleeping for 3 hour")
    time.sleep(3600)
else:
    db.close()
    print("***terminated***")


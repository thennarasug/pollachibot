import datetime as dt
import sqlite3
import time
import traceback
import logging
import Logger as log

# Twython twitter api
from twython import Twython, TwythonError
#heroku env variables
from os import environ

log.basicconfig("pollachibot", level=logging.INFO)

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
        cursor = db.execute(query)
        db.commit()
        return cursor
    except:
        error = traceback.print_exc()
        db.rollback()
        return None


# for database
dbfilewithpath = "./pollachi.db"
db = sqlite3.connect(dbfilewithpath)
create_table()

# heroku env variables
keywords = ['pollachi', 'பொள்ளாச்சி', 'pollachidistrict', 'பொள்ளாச்சிமாவட்டம்']

APP_KEY = environ.get('APP_KEY')
APP_SECRET = environ.get('APP_SECRET')
OAUTH_TOKEN = environ.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = environ.get('OAUTH_TOKEN_SECRET')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# indefinite while loop that runs every 1 hour. To remove the dependency on scheduler.
while True:
    count = 0
    trycount = 0
    totalcount = 0
    for keyword in keywords:
        for lang_list in ['en', 'ta']:
            for result_type in ['popular', 'mixed', 'recent']:
                try:
                    # count=100 max (default 15), result_type='mixed' or 'recent'
                    # count=15 max (default 15), result_type='popular'
                    search_results = twitter.search(q=keyword, count=100, lang=lang_list, result_type=result_type)

                    # print(search_results)
                    if len(search_results) > 0:
                        count = 0
                        for tweet in search_results['statuses']:

                            utf8Pollachi = keyword.lower().encode('utf-8')
                            totalcount = totalcount + 1
                            a = tweet['text'].lower().count("pollachi")
                            b = tweet['text'].lower().count("@pollachi")
                            c = tweet['text'].lower().count("_pollachi")
                            e = tweet['text'].lower().count("பொள்ளாச்சி")
                            d = tweet['user']['screen_name'].lower().count("pollachi")

                            # and utf8Pollachi in tweet['text'].lower().encode('utf-8')
                            #print(a + b + c + d, " == 0", a + e, " > ", b + c)
                            if (a + b + c + d == 0 or a + e > b + c) and tweet['user']['screen_name'].lower() not in ['signal_pollachi', 'pollachibot']:
                                try:
                                    cursor = select_error_string(tweet['id'])
                                    for row in cursor:
                                        if row[0] == 0:
                                            twitter.retweet(id=int(tweet['id']))
                                            print(tweet['user']['screen_name'], "-->", tweet['id'], "--->", keyword.lower(), "--->", tweet['text'].lower())
                                            log.loginfo(tweet['user']['screen_name'], "-->", tweet['id'], "--->", keyword.lower(), "--->", tweet['text'].lower())
                                            insert_error_string(tweet['id'])
                                            count = count + 1
                                            trycount = trycount + 1
                                            totalcount = totalcount + 1
                                            time.sleep(5)
                                        else:
                                            #print("already retweeted", tweet['id'], row[0])
                                            pass
                                except TwythonError as e:
                                    trycount = trycount + 1
                                    totalcount = totalcount + 1
                                    if "You have already retweeted this Tweet" in str(e):
                                        insert_error_string(tweet['id'])
                                        #print("already retweeted", tweet['id'])
                                        time.sleep(5)
                                    elif "blocked" in str(e):
                                        insert_error_string(tweet['id'])
                                        print("error on action ****blocked**** !!!", tweet['user']['screen_name'], tweet['id'], tweet['text'], e)
                                        log.logerror("error on action ****blocked**** !!!", tweet['user']['screen_name'], tweet['id'], tweet['text'], e)
                                    else:
                                        log.logerror("error on action!!!", e)
                                        print("error on action!!!", e)
                            else:
                                trycount = trycount + 1
                                totalcount = totalcount + 1

                        # print(keyword, "in", lang_list, "of", result_type, ". Total filtered and retweeted ---> ", str(count), " / ", str(trycount), " / ", str(totalcount))
                except TwythonError as e:
                    print("error on search", e)
                    log.logerror("error on search", e)
                except ConnectionResetError as c:
                    print("go to sleep..", c)
                    log.logerror("go to sleep..", c)
                    time.sleep(5)
                except Exception as e:
                    print("other errors ..", e)
                    log.logerror("other errors..", e)

            # added this to avoid "Twitter API returned a 429 (Too Many Requests), Rate limit exceeded"
            time.sleep(5)
    # print("end of search")
    log.loginfo("*****************************sleeping for 30min*****************************")
    print(dt.datetime.now(), "*****************************sleeping for 30 mins*****************************")
    time.sleep(60 * 30)


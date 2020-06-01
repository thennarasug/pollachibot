#Twython twitter api
from twython import Twython, TwythonError
#heroku env variables
from os import environ

import time
keywords =  ['pollachi','பொள்ளாச்சி']

APP_KEY = environ.get('APP_KEY')
APP_SECRET = environ.get('APP_SECRET')
OAUTH_TOKEN = environ.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = environ.get('OAUTH_TOKEN_SECRET')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


#indefinite while loop that runs every 1 hour. To remove the dependency on scheduler.
while True:
    count=0
    totalcount=0
    for keyword in keywords:
        for lang_list in ['en','ta']:
            try:
                #count=100 max (default 15), result_type='mixed' or 'recent'
                #count=15 max (default 15), result_type='popular'
                search_results = twitter.search(q=keyword,count=1000, lang=lang_list, result_type='recent')
            except TwythonError as e:
                print (e)

            for tweet in search_results['statuses']:

                utf8Pollachi=keyword.lower().encode('utf-8')
                totalcount = totalcount + 1
                #print("-------------------------")
                print(keyword, utf8Pollachi, tweet['user']['screen_name'], "-->", tweet['text'])
                #print("-------------------------")
                if "pollachi" not in tweet['user']['screen_name'] and "pollachi" not in tweet['user']['name'] and keyword.lower() not in tweet['user']['name'].lower() and utf8Pollachi in tweet['text'].lower().encode('utf-8'):
                #if  "RT @" not in tweet['text'] and tweet['retweeted'] == False and utf8Pollachi in tweet['text'].encode('utf-8'):
                #if  "RT @" not in tweet['text'] and tweet['retweeted'] == False and tweet['is_quote_status'] == False and utf8Pollachi in tweet['text'].encode('utf-8'):
                    try:
                        #print (tweet['text'])
                        twitter.retweet(id=int(tweet['id']))
                        count = count +1
                        print("*****************RT*******************")
                        #print ('Tweet from @%s Date: %s' % (tweet['user']['screen_name'].encode('utf-8'),tweet['created_at']))
                        #print (tweet['text'].encode('utf-8'), '\n')
                    except TwythonError as e:
                        print (e)


        print (keyword + "---> total filtered and retweeted ---> " + str(count) + " out of " + str(totalcount))
    print ("end of search")
    print ("sleeping for 30 minutes")
    time.sleep(1800)
else:
        print ("***terminated***")

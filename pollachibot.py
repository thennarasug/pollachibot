#Twython twitter api
from twython import Twython, TwythonError
#heroku env variables
from os import environ

import time
keywords =  ['pollachi','பொள்ளாச்சி'

APP_KEY = environ.get('APP_KEY')
APP_SECRET = environ.get('APP_SECRET')
OAUTH_TOKEN = environ.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = environ.get('OAUTH_TOKEN_SECRET')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#indefinite while loop that runs every 1 hour. To remove the dependency on scheduler.
while True:
    for keyword in keywords:
        for lang_list in ['en','ta']:
            try:
                search_results = twitter.search(q=keyword,count=100, lang=lang_list, result_type='recent')
            except TwythonError as e:
                print (e)
        count=0
        for tweet in search_results['statuses']:
            #if  "RT @" not in tweet['text'] and tweet['retweeted'] == :
            try:
                print (tweet['text'])
                twitter.retweet(id=int(tweet['id']))
                count = count +1
                print ('Tweet from @%s Date: %s' % (tweet['user']['screen_name'].encode('utf-8'),tweet['created_at']))
                print (tweet['text'].encode('utf-8'), '\n')
            except TwythonError as e:
                print (e)
        print ("total filtered and retweeted..." + str(count))
        print ("end of search")
    print ("sleeping for 1 hour")
    time.sleep(3600)
else:
        print ("***terminated***")

from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from PIL import Image,ImageDraw,ImageFont
import PIL
 

import twitter_credentials
import numpy as np
import pandas as pd
import os
import sys
import time




class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client


    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets


    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list



    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets



class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth




class TwitterStreamer():
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)





class TwitterListener(StreamListener):
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename


    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True    

    def on_error(self, status):
        if status == 420:
            return False
        print(status)



class TweetAnalyzer():  
    def tweets_to_data_frame(self, tweets):      
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets']) 
        return df


if __name__ == '__main__':
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    thechosen_user=sys.argv[1]
    tweets = api.user_timeline(screen_name=thechosen_user, count=10)  
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    pd.set_option('display.max_colwidth', -1)
    im = Image.new('RGB', (1200, 400), (255, 255, 255))
    for i in range(1,7):
        text1=str(df.head(i))
        font_type=ImageFont.truetype('Arial.ttf',20)
        draw=ImageDraw.Draw(im)
        draw.text(xy=(50,50),text=text1,fill=(0,0,0),font=font_type)
        im.save("img0"+str(i)+".PNG")
    cmd1="ffmpeg -r 1/3 -i img%02d.png -c:v libx264 -vf fps=25 -pix_fmt yuv420p tweets"+str(thechosen_user)+".mp4"
    os.system(cmd1)









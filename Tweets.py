import tweepy #https://github.com/tweepy/tweepy
import csv
import re
import os
import Data
import pytz
from datetime import datetime, timedelta, timezone

#Twitter API credentials
consumer_key='zph1TT3T7Ux6zGxU1SVzHNnkn'
consumer_secret='o7goTW2EAjnkwCKqbaTfncAXg1JlWyFuz7JQ8GkyRZwu8QtGaJ'
access_key='1094433381910163456-wBWM51cUHWfwaRykcOxGlaRIiJ14YV'
access_secret='ilPVSkXyBq2H3KTx92Beacvu4hQPd03WVtebabBj43iNe'

#regex for time extraction
time_extractor = re.compile(r'(\d\.?\d*)\s?(mins|min|hrs|hours|hr|hour)', flags=re.I)

#timezone
pst_tz = pytz.timezone('US/Pacific')

class Tweet():
	def __init__(self, created_at, text, id):
		self.wait_time = self.detect_time(text)
		self.created_at = self.fix_time(created_at)
		self.id = id

	def __str__(self):
		time = self.created_at
		return "{},{},{},{}\n".format(time.strftime("%a"), time.strftime("%x"), time.strftime("%I %p"), self.wait_time)

	def to_list(self):
		return [self.id, self.created_at.strftime("%Y-%m-%d %X"), self.wait_time]

	#Detect if a time is listed in the tweet
	def detect_time(self, text):
		wait_time = -1
		time_match = time_extractor.search(text)
		if time_match:
			wait_time = float(time_match.group(1))
			wait_time /= 60.0 if 'min' in time_match.group(2).lower() else 1
		return wait_time if wait_time > 0 else None

	#Fix the time to not be UTC
	#Then round it to nearest hour to make data cleaner
	def fix_time(self, created_at):
		utc_dt = pytz.utc.localize(created_at)
		created_at = pst_tz.normalize(utc_dt.astimezone(pst_tz))
		created_at += timedelta(minutes=30)
		created_at = created_at.replace(second=0, microsecond=0, minute=0)
		return created_at


class TwitterParser():

	def get_minmax_id(self):
		if not os.path.isfile("tweets.csv"): return None
		first = None
		with open("tweets.csv", "r") as csv_file:
			csv_reader = csv.reader(csv_file)
			first = next(csv_reader)
		return int(first[0]) if first else None

	def save_tweets(self, tweets):
		file_buffer = None
		if os.path.isfile("tweets.csv"):
			with open("tweets.csv", "r") as csv_file:
				file_buffer = csv_file.readlines()
		tweet_list = [tweet.to_list() for tweet in tweets]
		with open("tweets.csv", "w") as csv_file:
			csv_writer = csv.writer(csv_file)
			for tweet in tweet_list:
				csv_writer.writerow(tweet)
			if file_buffer:
				for line in file_buffer:
					csv_file.write(line)

	def get_latest_tweets(self, id=None):
		#Twitter only allows access to a users most recent 3240 tweets with this method

		#authorize twitter, initialize tweepy
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_key, access_secret)
		api = tweepy.API(auth)

		#initialize a list to hold all the tweepy Tweets
		alltweets = []

		#make initial request for most recent tweets (200 is the maximum allowed count)
		new_tweets = api.user_timeline(screen_name = 'howlinrays', count=200)

		#save most recent tweets
		#alltweets.extend(new_tweets)

		#save the id of the newest tweet
		oldest = new_tweets[0].id

		if not id:
			#keep grabbing tweets until there are no tweets left to grab
			while True:
				print("getting tweets before {}".format(oldest))

				new_tweets = api.user_timeline(screen_name = 'howlinrays', count=200, max_id=oldest)

				tweet_buf = [Tweet(tweet.created_at, tweet.text, tweet.id) for tweet in new_tweets]
				tweet_buf = [tweet for tweet in tweet_buf if tweet.wait_time]

				#save most recent tweets
				alltweets.extend(tweet_buf)

				#update the id of the oldest tweet less one

				print("...{} tweets downloaded so far".format(len(alltweets)))

				if not new_tweets: break
				oldest = new_tweets[-1].id - 1
		else:
			up_to_date = True if id == oldest else False
			while not up_to_date:
				new_tweets = api.user_timeline(screen_name = 'howlinrays', count=200, max_id=oldest)
				print("Not up to date. Most recent: {}, last recorded: {}".format(oldest, id))
				tweet_buf = [Tweet(tweet.created_at, tweet.text, tweet.id) for tweet in new_tweets]
				for tweet in tweet_buf:
					if tweet.id <= int(id):
						up_to_date = True
						break
					if tweet.wait_time: alltweets.append(tweet)

		return alltweets


if __name__ == '__main__':
	parser = TwitterParser()
	minmax_id = parser.get_minmax_id()
	tweets = parser.get_latest_tweets(minmax_id)
	parser.save_tweets(tweets)
	data = Data.Data().data_sort(num_days=31)
	averages = Data.Data().average_data(data)
	Data.Data().print_data(averages)

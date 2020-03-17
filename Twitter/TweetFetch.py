import tweepy #https://github.com/tweepy/tweepy

from Config import Secret
from Twitter.Tweet import Tweet

class TwitterParser():

	def __init__(self, db_instance):
		self.db_wrapper = db_instance
		tweets = self.get_latest_tweets()
		self.save_tweets(tweets)

	def save_tweets(self, tweets):
		for tweet in tweets:
			self.db_wrapper.insert_wait_time(tweet.id, tweet.created_at, tweet.wait_time)

	#TODO rewrite this section, my eyes are in pain
	def get_latest_tweets(self):
		#Twitter only allows access to a users most recent 3240 tweets with this method

		#authorize twitter, initialize tweepy
		auth = tweepy.OAuthHandler(Secret.consumer_key, Secret.consumer_secret)
		auth.set_access_token(Secret.access_key, Secret.access_secret)
		api = tweepy.API(auth)

		#initialize a list to hold all the tweepy Tweets
		alltweets = []

		#make initial request for most recent tweets (200 is the maximum allowed count)
		new_tweets = api.user_timeline(screen_name = 'howlinrays', count=200)

		#save most recent tweets
		#alltweets.extend(new_tweets)
		id = self.db_wrapper.get_last_wait_id()

		#save the id of the newest tweet
		oldest = new_tweets[0].id

		if not id:
			#keep grabbing tweets until there are no tweets left to grab
			#this only occurs if sql db is empty
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
			#keep fetching tweets until overlap detected from previously saved tweets
			up_to_date = True if id == oldest else False
			while not up_to_date:
				new_tweets = api.user_timeline(screen_name = 'howlinrays', count=200, max_id=oldest)
				tweet_buf = [Tweet(tweet.created_at, tweet.text, tweet.id) for tweet in new_tweets]
				for tweet in tweet_buf:
					if tweet.id <= int(id):
						up_to_date = True
						break
					if tweet.wait_time: alltweets.append(tweet)
				if alltweets:
					if not up_to_date:
						print("Not up to date. Most recent: {}, last recorded: {}".format(oldest, id))
					oldest = alltweets[-1].id - 1

		return alltweets

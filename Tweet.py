import pytz
import re

from datetime import datetime, timedelta, timezone

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

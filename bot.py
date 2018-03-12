import random
import datetime
import time
import traceback

import praw

import login
import weekly_topics


def update_log(id, log_path): #para los comentarios que ya respondi
	with open(log_path, 'a') as my_log:
			my_log.write(id + "\n")

def load_log(log_path): #para los comentarios que ya respondi
	with open(log_path) as my_log:
		log = my_log.readlines()
		log = [x.strip('\n') for x in log]
		return log

def output_log(text): #lo uso para ver el output del bot
	output_log_path = "output_log.txt"
	with open(output_log_path, 'a') as myLog:
		s = "[" +  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
		s = s + text +  "\n"
		myLog.write(s)

def is_date_holiday(date):
	d = date.day
	m = date.month
	for date_key in weekly_topics.holidays.keys():
		if date_key == (m, d):
			return True, weekly_topics.holidays[date]
	return False, None

def is_today_holiday():
	return is_date_holiday(datetime.datetime.today())

if __name__ == "__main__":

	days = [
		'Lunes',
		'Martes',
		'Miercoles',
		'Jueves',
		'Viernes',
		'Sabado',
		'Domingo'
		]

	log_path = 'log.txt'

	try:
		output_log('Comenzando el script')
		reddit = praw.Reddit(
			client_id = login.client_id,
			client_secret = login.client_secret,
			password = login.password,
			username = login.username,
			user_agent = 'testscript for /u/random_daily_subject')

		is_holiday, post = is_today_holiday()
		if is_holiday:
			today = post[0]
			body = post[1]
		else:
			log = load_log(log_path)
			while True:
				today = random.choice(list(weekly_topics.topics.keys()))
				if today not in log[-6:]:
					break
			body = weekly_topics.topics[today]
		update_log(today, log_path)

		title = days[datetime.datetime.today().weekday()] \
				+ ' de ' + today + '.'
		body = body + "\n\n*****\n\n"
		body = body + "*Another bot by \/u/DirkGentle.* "
		body = body + "[Source](https://github.com/dirkgentle/random_daily_subject)."
		output_log(title)
		output_log(body)
		reddit.subreddit('ROU').submit(title, selftext=body)

	except Exception as exception:
		output_log(str(exception))
		output_log(traceback.format_exc())

import json
import requests
import urllib.request as req
import urllib.error
import pathlib
import datetime
import sys
from time import sleep
from pathlib import Path

home = str(Path.home())
now = datetime.datetime.now()

def main():
	subreddit = input('What subreddit do you want to download from? ')
	if len(sys.argv) > 1 and sys.argv[1] == 'top':
		response = requests.get(f'https://reddit.com/r/{subreddit}/top.json?t=all')	
	else:
		response = requests.get(f'https://reddit.com/r/{subreddit}.json')
	while response.status_code != 200:
		print('Waiting for reddit API...', end='\r', flush=True)
		if len(sys.argv) > 1 and sys.argv[1] == 'top':
			response = requests.get(f'https://reddit.com/r/{subreddit}/top.json?t=all')	
		else:
			response = requests.get(f'https://reddit.com/r/{subreddit}.json')
		sleep(1) #because reddit's API is rate limited
	
	posts = json.loads(response.content.decode('utf-8'))
	posts = posts['data']['children']
	numPosts = len(posts)
	count = 1
	numDownloaded = 0
	for post in posts:
		print(f'Response received! On post {count}/{numPosts} now.', end='\r', flush=True)
		if post['data']['is_self'] == False:
			url = post['data']['url']
			title = post['data']['title']
			datetime = now.strftime("%Y-%m-%d %H:%M")
			pathlib.Path(f'{home}/Downloads/reddit-dl/{subreddit}/{datetime}').mkdir(parents=True, exist_ok=True)
			if post['data']['domain'] == 'gfycat.com':
				try:
					gfyurl = url.rsplit('/',1)[1]
					gfyres = requests.get(f'https://api.gfycat.com/v1/gfycats/{gfyurl}')
					gfyjson = json.loads(gfyres.content.decode('utf-8'))
					gfymp4 = gfyjson['gfyItem']['mp4Url']
					req.urlretrieve(gfymp4, f'{home}/Downloads/reddit-dl/{subreddit}/{datetime}/{title}')
					numDownloaded += 1
				except urllib.error.HTTPError as err:
					print('Rate limited by the reddit API, trying again in 2 seconds...')
					sleep(2)
					try:
						req.urlretrieve(url, f'{home}/Downloads/reddit-dl/{subreddit}/{datetime}/{title}')
						numDownloaded += 1
					except urllib.error.HTTPError as err:
						print('Still rate limited, skipping current image')
				except KeyError:
					print('Image deleted, skipping it.')

			else:
				try:
					req.urlretrieve(url, f'{home}/Downloads/reddit-dl/{subreddit}/{datetime}/{title}')
					numDownloaded += 1
				except urllib.error.HTTPError as err:
					print('Rate limited by the reddit API, trying again in 2 seconds...')
					sleep(2)
					try:
						req.urlretrieve(url, f'{home}/Downloads/reddit-dl/{subreddit}/{datetime}/{title}')
						numDownloaded += 1
					except urllib.error.HTTPError as err:
						print('Still rate limited, skipping current image')

		count += 1
#sleep(2) #because reddit's API is rate limited
	print(f'{numDownloaded} total images downloaded!')
	
main()

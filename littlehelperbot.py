#!/usr/bin/python2.7 -u

import bs4
import praw
import re
import requests

from littlehelper_config import *

reddit = praw.Reddit(user_agent = USER_AGENT)
reddit.login(REDDIT_USERNAME, REDDIT_PASS)
comment_stream = praw.helpers.comment_stream(reddit, "all", verbosity=1)

def got_one(comment):

	print "==============="

	print comment.permalink.encode('utf-8')

	# body_html is escaped html. Unescape it here.
	soup = bs4.BeautifulSoup(comment.body_html)
	unescaped = soup.get_text()

	print unescaped.encode('utf-8')

	# And now actually parse it.
	soup = bs4.BeautifulSoup(unescaped)

	links = []
	for link in soup.find_all('a'):
		href = link.get('href')
		text = link.text
		if href.find("m.wikipedia.org") != -1:
			new_href = re.sub("m.wikipedia.org", "wikipedia.org", href)
			new_text = re.sub("m.wikipedia.org", "wikipedia.org", text)

			new_href = re.sub("\(", "\\\(", new_href)
			new_href = re.sub("\)", "\\\)", new_href)

			new_text = re.sub("\[", "\\\[", new_text)
			new_text = re.sub("\]", "\\\]", new_text)

			links.append((new_text, new_href))
			print ">>>>> %s %s -> %s %s" % (href.encode('utf-8'), text.encode('utf-8'),
				new_href.encode('utf-8'), new_text.encode('utf-8'))

	if comment.author.name != "LittleHelperRobot" and len(links) > 0:
		if len(links) == 1:
			text = "Non-mobile: [%s](%s)\n\n" % links[0]
			text += "^I'm ^a ^robot, ^and ^this ^is ^my ^purpose. ^Thank ^you ^for ^all ^the ^kind ^replies! ^PM ^/u/xl0 ^if ^I'm ^causing ^any ^trouble!"
		else: # len(links) > 1
			text = "Non-mobile:\n\n"
			for link in links:
				text += " * [%s](%s)\n" % (link)
			text += "\n^I'm ^a ^robot, ^and ^this ^is ^my ^purpose. ^Thank ^you ^for ^all ^the ^kind ^replies! ^PM ^/u/xl0 ^if ^I'm ^causing ^any ^trouble!"
		print "I'm commenting:\n", text.encode('utf-8')
		try:
			c = comment.reply(text);
			print c.permalink.encode('utf-8')
		except praw.errors.RateLimitExceeded as e:
			print "Nope, rate limit exceded:", str(e)
		except praw.errors.APIException as e:
			print "Some other exception:", str(e)
		except requests.exceptions.HTTPError as e:
			print "Looks like we are banned here"

n = 0
for comment in comment_stream:
	n += 1
	if not n % 1000:
		print n

	if comment.body.lower().find("m.wikipedia.org") != -1:
		got_one(comment)



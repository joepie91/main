#!/usr/bin/python
start_page = "http://www.devilskitchen.me.uk/"
default_headers = {
	'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13",
	'Referer': start_page
}
date_regex = '(?P<month>[0-9]{1,2})\/(?P<day>[0-9]{1,2})\/(?P<year>[0-9]{4})\s(?P<hour>[0-9]{1,2})[:.](?P<minute>[0-9]{1,2})[:.](?P<second>[0-9]{1,2})\s(?P<period>AM|PM)'

import re, urllib2, datetime, argparse, os, json, time
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Archive posts for devilskitchen.me.uk in JSON format')

parser.add_argument('-O', dest='output_dir', action='store', default='.',
                   help='output directory for archived posts')

args = parser.parse_args()
options = vars(args)

try:
	os.mkdir(options['output_dir'])
except:
	pass

def fetch_page_headers(url, headers):
	request = urllib2.Request(url, headers=headers)
	opener = urllib2.build_opener()
	response = opener.open(request)
	return (response.code, response.headers, response.read())

def fetch_archives():
	status_code, headers, response = fetch_page_headers(start_page, default_headers)
	
	if status_code == 200:
		archive_pages = re.findall("http:\/\/www\.devilskitchen\.me\.uk\/[0-9]{4}_[0-9]{2}_[0-9]{2}_archive\.html", response)
		
		for page in archive_pages:
			print "Scraping %s..." % page
			fetch_articles(page)
			time.sleep(20)
	else:
		print "ERROR: Failed to retrieve archive index! Exiting..."
		exit(1)
		

def fetch_articles(url):
	status_code, headers, response = fetch_page_headers(url, default_headers)
	
	if status_code == 200:
		soup = BeautifulSoup(response)
		posts = soup.find_all("div", class_="post")
		
		for post in posts:
			try:
				post_title = post.h5.string
			except AttributeError, e:
				print "WARNING: Article with missing title"
				post_title = ""
			
			author_details = post.find_all("p", class_="author-details")[0]
			author_name = author_details.find_all("span", class_="author-name")[0].string
			post_date = author_details.find_all("a")[0].string
			post_body = post.find_all("div", class_="post-body")[0].div.prettify()
			
			actual_date = datetime.datetime.strptime(post_date, "%m/%d/%Y %I:%M:%S %p")
			
			try:
				os.mkdir("%s/%d-%d" % (options['output_dir'], actual_date.year, actual_date.month))
			except:
				pass
			
			try:
				json_file = open("%s/%d-%d/%d-%d-%d-%d-%d-%d.json" % (options['output_dir'], actual_date.year, actual_date.month, actual_date.year, 
					actual_date.month, actual_date.day, actual_date.hour, actual_date.minute, actual_date.second), 'w')
				
				json.dump({
					'title': post_title,
					'date': actual_date.isoformat(),
					'author': author_name,
					'body': post_body
				}, json_file)
				
				json_file.close()
			except:
				raise
				
			
			print "Archived '%s', posted at %s by %s" % (post_title, actual_date.isoformat(), author_name)
	else:
		print "ERROR: Failed to retrieve %s! Status code was %d" % (url, status_code)

#soup = BeautifulSoup(html_doc)
fetch_archives()

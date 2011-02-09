#!/usr/bin/env python
#-*- coding:utf-8 -*-

import libxml2dom
import urllib
import re
import os
import threading
import xapian
import string
from collections import deque
import time


que = deque()
finished = 0

class IndexerThread(threading.Thread):
	def __init__(self):
		self.database = xapian.WritableDatabase("xapian/", xapian.DB_CREATE_OR_OPEN)
		self.indexer = xapian.TermGenerator()
		self.stemmer = xapian.Stem("romanian")
		self.indexer.set_stemmer(self.stemmer)
		threading.Thread.__init__(self)

	def run(self):
		global que
		while 1:
			if len(que) != 0:
				data, url = que.popleft()
				
				doc = xapian.Document()
				doc.set_data(url)
				
				doc.add_value(0,url)
				doc.add_value(1,"Infoarena")
				#FIXME:doc.add_value(DATE_ADDED,)

				self.indexer.set_document(doc)
				self.indexer.index_text(data)

				# Add the document to the database.
				self.database.add_document(doc)
				print "Indexed ",url
			while len(que) == 0:
				time.sleep(0.01)
				if finished:
					break
			
			if finished and len(que) == 0 and threading.active_count() == 2:
				break				
		print "Indexing finished, que length", len(que)
		
		

class ScraperThread(threading.Thread):
	def __init__ (self, problem):
		self.problem = problem
		threading.Thread.__init__(self)
	def run(self):
		global que
		problem = self.problem
		data = get_problem(problem[1]), problem[1]
		que.append(data)
                # Add the document to the databaseself.
                print "Got ",problem[0]

def get_problems(page):
	problems = []
	data = urllib.urlopen("http://infoarena.ro/arhiva?display_entries=250&first_entry="+str(250*page))
	s = data.read()
	doc = libxml2dom.parseString(s, html=1)
	a_elements = doc.getElementsByTagName("a")
	for node in a_elements:
		if re.match('^\/problema.*',node.getAttribute("href")):
			problems.append(node.getAttribute("href"))

	problems = list(set(problems)) #getting rid of duplicates caused by open problems who have another link
	for i in range(len(problems)):
		problems[i] = [problems[i], "http://infoarena.ro"+problems[i]]
	return problems

def get_problem(url):
	data = urllib.urlopen(url)
	s = data.read()
	print "Got",len(s)," data form server."
	doc = libxml2dom.parseString(s,html=1)
	main = doc.getElementById("main")
	for node in main.childNodes:
		if  node.getAttribute("class") == "wiki_text_block":
			return node.toString()

#Logic that I can't put in a clas...
indexer = IndexerThread()
indexer.start()
thread_limit = 40

#Or maybe I should start from here :P
i = 0
problems = ['a']
while len(problems) != 0:
	problems = get_problems(i)
	i+=1
	print "Processing page ",i,"..."
	for problem in problems:
		while threading.active_count() > thread_limit+2:
			time.sleep(0.01)
		ScraperThread(problem).start()
		
finished = 1
		


#!/usr/bin/env python
#-*- coding:utf-8 -*-

import libxml2dom
import urllib
import re
import os

def get_problems(page):
	problems = []
	data = urllib.urlopen("http://infoarena.ro/arhiva?display_entries=50&first_entry="+str(50*page))
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
	doc = libxml2dom.parseString(s,html=1)
	main = doc.getElementById("main")
	for node in main.childNodes:
		if  node.getAttribute("class") == "wiki_text_block":
			return node.toString()
i = 0
problems = ['a']
while len(problems) != 0:
	problems = get_problems(i)
	i+=1
	print "Processing page ",i,"..."
	for problem in problems:
		#f = open("/dev/null",'w')
		cucu = get_problem(problem[1])
		print "Got ",problem[0]
		

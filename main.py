#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os

### Importing Google App API Library 
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

### Importing Standard Library
import random, re, logging, time

### Importing User Library
from BeautifulSoup import BeautifulSoup

class MainHandler(webapp2.RequestHandler):

	def get(self):
		if(os.environ.has_key('SERVER_SOFTWARE')):
			if("Development" in os.environ.get('SERVER_SOFTWARE')):
				my="my.js"
				animation="animation.js"
			else:
				my="my.min.js"
				animation="animation.min.js"
		else:
			logging.error("This environment is weird.")

		header='''
<!DOCTYPE html>
	<html>
	 <head>
	  <title>transatonce</title>
	  <script type='text/javascript' src='js/%s'></script>
	  <script type='text/javascript' src='js/%s'></script>
	  <script type='text/javascript' src='js/jquery-2.1.1.min.js'></script>
	  <script type='text/javascript'>
	  	document.onkeyup=onKeyUp;
	  	imageLoader();
	  </script>
	 </head>

	 <body>
''' % (my,animation)

		cont = '''
	  <a href="images/test.png" border=1>What is this?</a><br>
	  <br>

	  <form action="#" name=trans>
	   <textarea name=text rows=5 cols=20" onChange="count()" onClick="ask()"></textarea><br>
	   <input type=button name=input value="Go" onClick="makeQueries()">
	   <br>
	   <input type=radio name=site value=alc checked>alc
	   <input type=radio name=site value=goo>goo
	   <input type=radio name=site value=longman>longman
	   <br>
	   <input type=checkbox name=increment onClick="explain('increment')">incremental
	   <input type=checkbox name=notice onClick="explain('notice')" checked hidden>
	  </form>

	  <div id=disp_parent></div>
'''

		footer='''
	 </body>
	</html>
'''

		self.response.out.write(header+cont+footer)
	
class TransHandler(webapp2.RequestHandler):

	def post(self):

		url = {}
		url["alc"] = "http://eow.alc.co.jp/%s/utf-8/"
		url["goo"] = "http://dictionary.goo.ne.jp/srch/ej/%s/m0u/"
		url["longman"]="http://www.ldoceonline.com/dictionary/%s"

		regex = {}
		regex["alc"] = {"id":"resultsList"}
		regex["goo"] = {"class":"allList"}
		regex["longman"] = {"class":"Entry"}

		color = {}
		color["alc"] = "crimson"
		color["goo"] = "sienna"
		color["longman"] = "navy"

		def getdict(site,divs):

			if site=="alc":
				dicttrans= divs.find("div")

			elif site=="goo":
				a=divs.find("dt").find("a")
				href=a.get("href")
				goourl='/'.join(url[site].split("/")[:3])
				page=" <a href=\""+goourl+href+"\" target=\"_blank\">-></a>"
				dicttrans=str(divs.find("dd").string)+page.encode('utf-8')

			elif site=="longman":
				div=""
				for cdivs in divs.findAll("div",{"class":"Sense"}):
					for d in cdivs.contents:
						try:
							if d['class'] == 'numsense': continue
							if d['class'] == 'FIELD': continue
						except:
							# Key error for 'class'
							pass

						div+=str(d)

				dicttrans=div.replace("src=\"","src=\""+'/'.join(url[site].split("/")[:3]))

			return dicttrans

		def gettag(site,result):

			soup = BeautifulSoup(result.content)
			if site=="goo":
				tag = soup.find("dl",regex[site])
			elif site=="XXX":
				#tag = soup.find("xxx",regex[site])
				pass
			else:
				tag = soup.find("div",regex[site])

			return tag

		# if it is incapable of Japanese
		def isjaincap(site,w):
			if site!="alc":
				for _w in w:
					if ord(_w)>255:
						return True

			return False

		w = self.request.get('word')
		site = self.request.get('site')

		logging.info("site:"+site+", word:"+w)

		if w == "" or site == "":
			self.response.out.write("")
			return

		# save w
		ws = w

		# to store the result to show
		text=""

		if isjaincap(site,w):
			text="<b>\"alc\"を選んでください.</b>"

		delay=1
		while delay < 10 and text=="":

			try:
				wr = w.replace(" ","%20")
				result = urlfetch.fetch(url[site]%wr)
			except Exception as e:
				logging.error(str(type(e))+" "+str(e.args))
				text="%s might not be available now."%site
				break

			if result.status_code==200:

				try:
					tag = gettag(site,result)
					dicttrans = getdict(site,tag)

				except Exception as e:
					logging.error(str(type(e))+" "+str(e.args)+"\nsite:"+site+", word:"+w)

					if site=="longman" and delay==1:
						w=w+"_1"
					else:
						text="No word matched."
						break

				else:
					text=dicttrans
					break
			else:
				pass
				# Try again after sleep

			time.sleep(delay)
			delay*=2

		if delay >= 10:
			text="Failed to retrieve."

		wsout =""
		sp = "&nbsp;"

		wsout+="<br><font size=5>"+ws.encode('utf-8')+"</font>"
		wsout+=sp*3

		wsout+="<font size=2 color=white style=background-color:"+color[site]+">"
		wsout+=sp*2
		wsout+=site.encode('utf-8')
		wsout+=sp*2
		wsout+="</font><hr>"

		wsout+=str(text)

		self.response.out.write(wsout)


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/trans',TransHandler)
], debug=True)

util.run_wsgi_app(app)


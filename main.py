#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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
				js="my.js"
			else:
				js="my.min.js"
		else:
			logging.error("This environment is weird.")

		header='''
<!DOCTYPE html>
	<html>
	 <head>
	  <title>transatonce</title>
	  <script type='text/javascript' src='js/%s'></script>
	  <script type='text/javascript' src='js/jquery-2.1.1.min.js'></script>
	  <script type='text/javascript'>
	   document.onkeyup=function(e){
		   if(!document.forms['trans'].elements['input'].disabled){
			   if(e.keyCode==27){ // ESC:27
				   deleteElement('disp_parent');
		           document.trans.text.value="";
			   }
		   }
	   };
	  </script>
	  
	 </head>

	 <body>
''' % js

		cont = '''
	  <font size=5>Translate through dictionary site at once.</font><br><hr>
	  Note : One line, one phrase. ESC will clear all the text.<br>
	  <br>
	  <img src="image/test.png" width="50%" border=1><br>
	  <br>

	  <form action="#" name=trans>
	   <textarea name=text rows=5 cols=20" onChange="count()"></textarea><br>
	   <input type=button name=input value="Translate" OnClick="makeQuery()">
	   <br>
	   <input type=radio name=site value=alc checked>alc
	   <input type=radio name=site value=goo>goo
	   <input type=radio name=site value=longman>longman
	   <br>
	   <input type=checkbox name=append>append
	   <input type=checkbox name=notice checked>notice
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

		if w == "" or site == "":
			self.response.out.write("")
			return

		# save w
		ws = w

		# to store the result to show
		text=""

		if isjaincap(site,w):
			text="<b>Please choose alc for the translation from Japanese to English.</b>"

		delay=1
		while delay < 10 and text=="":

			wr = w.replace(" ","%20")
			result = urlfetch.fetch(url[site]%wr)

			if result.status_code==200:

				try:
					tag = gettag(site,result)
					dicttrans = getdict(site,tag)

				except Exception as e:
					logging.error(str(type(e))+"\n"+str(e.args)+"\n"+e.message)

					if site=="longman" and delay==1:
						w=w+"_1"
					else:
						text="No word matched."
						break

				else:
					text=dicttrans
					break

			time.sleep(delay)
			delay*=2

		if delay >= 10:
			text="Failed to retrieve."

		wsout =""
		wsout+="<br><br><font size=5>"+ws.encode('utf-8')+"</font>"
		wsout+="&nbsp;&nbsp;&nbsp;<font size=2 color=white style=background-color:"+color[site]+">&nbsp;&nbsp;"+site+"&nbsp;&nbsp;</font><hr>"

		self.response.out.write(wsout)
		self.response.out.write(text)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/trans',TransHandler)
], debug=True)

util.run_wsgi_app(app)


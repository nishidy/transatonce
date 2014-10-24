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

### Importing Google App API Library 
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

### Importing Standard Library
import random, re, logging, time

### Importing User Library
from BeautifulSoup import BeautifulSoup

class MainHandler(webapp2.RequestHandler):

    def get(self):

		header='''
<!DOCTYPE html>
	<html>
	 <head>
	  <title>transatonce</title>
	  <script type='text/javascript' src='js/my.js'></script>
	  <script type='text/javascript' src='js/jquery-2.1.1.min.js'></script>
	  <script type='text/javascript'>
	   document.onkeyup=function(e){
		   if(e.keyCode==27){ // ESC:27
			   deleteElement('disp_parent');
	           document.trans.text.value="";
		   }
	   };
	  </script>
	  
	 </head>

	 <body>
'''

		cont = '''
	  <font size=5>Translate through dictionary site at once.</font><br><hr>
	  Note : One line, one phrase. ESC will clear the text.<br>
	  <br>

	  <form action="#" name=trans>
	   <textarea name=text rows=5 cols=20" onChange="count()"></textarea><br>
	   <input type=button name=input value="Translate" OnClick="makeQuery()">
	   <input type=radio name=site value=alc checked>alc
	   <input type=radio name=site value=goo>goo
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

		regex = {}
		regex["alc"] = "resultsList"
		regex["goo"] = "allList"

		def getdict(site,divs):

			if site=="alc":
				dictword = str(divs.find("span"))
				dicttrans= divs.find("div")
			elif site=="goo":
				a=divs.find("dt").find("a")
				dictword=a.string

				href=a.get("href")
				goourl='/'.join(url[site].split("/")[:3])
				page=" <a href=\""+goourl+href+"\" target=\"_blank\">-></a>"
				dicttrans=str(divs.find("dd").string)+page.encode('utf-8')

			return dictword,dicttrans

		def gettag(site,result):

			soup = BeautifulSoup(result.content)

			if site=="alc":
				tag = soup.find("div",id=re.compile(regex[site]))
			elif site=="goo":
				tag = soup.find("dl",{"class":regex[site]})

			return tag

		w = self.request.get('word')
		site = self.request.get('site')
		if w == "" or site == "":
			self.response.out.write("")
			return

		delay=1
		while delay < 10:

			wr = w.replace(" ","%20")
			result = urlfetch.fetch(url[site]%wr)

			if result.status_code==200:

				tag = gettag(site,result)

				try:
					dictword,dicttrans = getdict(site,tag)

				except Exception as e:
					logging.error(str(type(e))+"\n"+str(e.args)+"\n"+e.message)

					# To show word
					self.response.out.write(
							"<br><br><font size=5>"+\
							w.encode('utf-8')+\
							"</font><hr>No word matched.")

					break

				else:
					# To show word
					self.response.out.write(
							"<br><br><font size=5>"+\
							dictword.encode('utf-8')+\
							"</font><hr><br>")

					# To show translation
					self.response.out.write(dicttrans)

					break

			else:
				pass

			time.sleep(delay)
			delay*=2

		if delay < 10:
			pass

		else:
			self.response.out.write(
					"<br><br><font size=5>"+\
					w.encode('utf-8')+\
					"</font><hr><br>Failed to retrieve...")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/trans',TransHandler)
], debug=True)

util.run_wsgi_app(app)


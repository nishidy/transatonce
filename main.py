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
	  
	 </head>

	 <body>
'''

		cont = '''
	  <font size=5>Translate through alc at once.</font><br><hr>
	  You can translate many words through alc at once.<br>
	  Each result will follow to show one by one under the button.<br>
	  <br>

	  <form action="#" name=trans>
	   <textarea name=text rows=5 cols=20" onChange="count()"></textarea><br>
	   <input type=button value="Translate altogether" OnClick="makeEachQuery()">
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

		words = self.request.get('words')

		delay=1
		for w in words.split('\n'):

			if w == "": continue 

			ww = w.replace(" ","%20")
			result = urlfetch.fetch("http://eow.alc.co.jp/"+ww+"/utf-8/")

			if result.status_code==200:

				delay=1

				soup = BeautifulSoup(result.content)
				divs = soup.find("div",id=re.compile("resultsList"))

				try:
					span = divs.find("span")
					div  = divs.find("div")

				except:
					self.response.out.write("<br><br><font size=5>"+\
						 w.encode('utf-8')+\
						 "</font><hr><br>")
					continue
				else:
					self.response.out.write("<br><br><font size=5>"+\
						 str(span).encode('utf-8')+\
						 "</font><hr><br>")
					self.response.out.write(div)
					#time.sleep(0.3)

				finally:
					pass
			else:

				self.response.out.write("<br><br><font size=5>"+\
					w.encode('utf-8')+\
					"</font><hr><br>")
				time.sleep(delay)
				delay*=2


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/trans',TransHandler)
], debug=True)

util.run_wsgi_app(app)


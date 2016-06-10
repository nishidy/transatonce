#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
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
from retrying import retry

class MainHandler(webapp2.RequestHandler):

    def get(self):

        # minify command was locally installed by 'npm install -g minifier'
        if(os.environ.has_key('SERVER_SOFTWARE')):
            if("Development" in os.environ.get('SERVER_SOFTWARE')):
                my_js="my.js"
                animation_js="animation.js"
            else:
                my_js="my.min.js"
                animation_js="animation.min.js"
        else:
            logging.error("This environment is wierd.")

        meta_tag=""
        if(os.environ.has_key('HTTP_USER_AGENT')):
            agent=os.environ.get('HTTP_USER_AGENT')
            if("iPhone" in agent) or ("iPad" in agent) or ("Android" in agent) or\
              ("iphone" in agent) or ("ipad" in agent) or ("android" in agent):
                meta_tag="<meta name=viewport content=width=device-width>"

        html=open("html/main.html").read().format(
            meta=meta_tag,
            my=my_js,
            animation=animation_js
        )

        self.response.out.write(html)

class TransHandler(webapp2.RequestHandler):

    def post(self):

        url = {
            "alc": "http://eow.alc.co.jp/%s/utf-8/",
            "goo": "http://dictionary.goo.ne.jp/srch/all/%s/m0u/",
            "longman": "http://www.ldoceonline.com/dictionary/%s",
        }

        regex = {
            "alc": {"id": "resultsList"},
            "goo": {"class": "allList"},
            "longman": {"class": "Entry"}
        }

        color = {
            "alc": "crimson",
            "goo": "sienna",
            "longman": "navy"
        }

        def parseTags(site,tags_info):

            if site=="alc":
                parsed_result=tags_info.find("div")

            elif site=="goo":
                a=tags_info.find("dt").find("a")
                href=a.get("href")
                goourl='/'.join(url[site].split("/")[:3])
                page=" <a href=\""+goourl+href+"\" target=\"_blank\">-></a>"
                parsed_result=str(tags_info.find("dd").string)+page.encode('utf-8')

            elif site=="longman":
                div=""
                for ctags_info in tags_info.findAll("div",{"class":"Sense"}):
                    for d in ctags_info.contents:
                        try:
                            if d['class'] == 'numsense': continue
                            if d['class'] == 'FIELD': continue
                        except:
                            # Key error for 'class'
                            pass
                        div+=str(d)

                parsed_result=div.replace("src=\"","src=\""+'/'.join(url[site].split("/")[:3]))

            return parsed_result

        def getTagsInfo(site,fetched):

            soup = BeautifulSoup(fetched.content)
            if site=="goo":
                tag = soup.find("dl",regex[site])
            elif site=="XXX":
                #tag = soup.find("xxx",regex[site])
                pass
            else:
                tag = soup.find("div",regex[site])

            return tag

        def isIncapableOfJap(site,word):
            if site!="alc":
                for char in word:
                    if ord(char)>255:
                        return True

            return False

        @retry(wait_exponential_multiplier=1000,stop_max_attempt_number=3)
        def doUrlFetch(word):

            try:
                fetched = urlfetch.fetch(url[site]%word.replace(" ","%20"), deadline=10)
            except Exception as e:
                logging.error(str(type(e))+" "+str(e.args))
                raise e

            if fetched.status_code==200:
                try:
                    tags_info = getTagsInfo(site,fetched)
                    parsed_result= parseTags(site,tags_info)
                except Exception as e:
                    logging.error(str(type(e))+" "+str(e.args)+"\nsite:"+site+", word:"+word)
                    return ""
                else:
                    return parsed_result
            else:
                raise Exception("Returned status code was not 200, %d."%(fetched.status_code));


        word = self.request.get('word')
        site = self.request.get('site')

        logging.info("site:"+site+", word:"+word)

        if word == "" or site == "":
            self.response.out.write("")
            return

        # This is the text to show
        text=""

        if isIncapableOfJap(site,word):
            resp_result = "<b>日本語からの訳は, \"alc\"が対応しています.</b>"
        else:
            resp_result = doUrlFetch(word)

        resp_template=""
        nbsp = "&nbsp;"

        resp_template+="<br><font size=5>"+word.encode('utf-8')+"</font>"
        resp_template+=nbsp*3
        resp_template+="<font size=2 color=white style=background-color:"+color[site]+">"
        resp_template+=nbsp*2
        resp_template+=site.encode('utf-8')
        resp_template+=nbsp*2
        resp_template+="</font><hr>"
        resp_template+="訳語の取得に失敗しました." if resp_result=="" else str(resp_result)

        self.response.out.write(resp_template)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/trans',TransHandler)
], debug=True)

util.run_wsgi_app(app)


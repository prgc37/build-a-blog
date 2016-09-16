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
import os
import webapp2
import jinja2

from google.appengine.ext import db 

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Entries(db.Model):
	title = db.StringProperty(required= True)
	entry = db.TextProperty(required= True)
	posted = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
	def render_post(self, title="", entry="", error=""):

		self.render("bloghome.html", title=title, entry=entry, error=error)

	def get(self):
		self.render_post()

	def post(self):
		title = self.request.get("title")
		entry = self.request.get("entry")
		if title and entry:
			e = Entries(title = title, entry = entry)
			e.put()
			self.redirect('/blog/' + str(e.key().id()))
		else:
			error = "We need both a title and a blog entry por favor! "
			self.render_post(title, entry, error)

class MainPage(Handler):
	def render_main(self, title="", entry=""):
		entries5 = db.GqlQuery("SELECT * FROM Entries "
							  "ORDER BY posted DESC "
							  "LIMIT 5" ) 
								
		self.render("blogfull.html", title=title, entry=entry, entries5=entries5)

	def get(self):
		self.render_main()

class ViewPostHandler(Handler):
	def render_one(self, title="", entry="", error=""):
		self.render("blogone.html", title=title, entry=entry)

	def get(self, id):
		onePost = Entries.get_by_id(int(id))
		self.render_one(title=onePost.title, entry=onePost.entry)

	def post(self):
		if not onePost:
			error = "If you could give us a valid ID number...that would be greeeeeeeat."
			self.render_one(title, entry, error)
		else:
			self.redirect('/blog/' + str(e.key().id())) 



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

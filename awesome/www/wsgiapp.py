#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A WSGI application entry.
'''

import logging

logging.basicConfig(level=logging.INFO)

import os, time
from datetime import datetime

from transwarp import db
from transwarp.web import WSGIApplication, Jinja2TemplateEngine

from config import configs

def datetimetillnow_filter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return u'1 minute ago'
	if delta < 3600:
		return u'%s minutes ago' % (delta//60)
	if delta < 86400:
		return u'%s %s ago' % (delta//3600, 'hours' if delta//3600>1 else 'hour')
	if delta < 604800:
		return u'%s %s ago' % (delta//86400, 'days' if delta//86400>1 else 'day')
	dt = datetime.fromtimestamp(t)
	return u'%s-%s-%s' % (dt.year, dt.month, dt.day)

def datetime_filter(t):
	lt = time.localtime(t)
	return u'%s' % time.strftime("%b %d, %Y ",lt)

def num_datetime_filter(t):
	lt = time.localtime(t)
	return u'%s' % time.strftime("%Y-%m-%d",lt)

# init db:
db.create_engine(**configs.db)

# init wsgi app:
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))
# init Jinja2 template engine
template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
template_engine.add_filter('datetime', datetime_filter)
template_engine.add_filter('numdatetime', num_datetime_filter)
template_engine.add_filter('datetimetillnow', datetime_filter)

wsgi.template_engine = template_engine

# load url func with @get and @post
import urls
wsgi.add_module(urls)
wsgi.add_interceptor(urls.manage_interceptor)

# start the server at port 9000
if __name__ == '__main__':
	wsgi.run(port=9000, host='0.0.0.0')
else:
	application = wsgi.get_wsgi_application()
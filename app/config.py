#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Configuration
'''

import config_default

class Dict(dict):
	'''
	Simple dict but support access as x.y style.
	'''
	def __init__(self, names=(), values=(), **kw):
		super(Dict, self).__init__(**kw)
		for k, v in zip(names, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

def merge(defaults, override):
	'''
	if the override and the default have the same key
	override the default with value of override
	'''
	r = {}
	for k,v in defaults.iteritems():
		if k in override:
			if isinstance(v, dict):
				r[k] = merge(v, override[k])
			else:
				r[k] = override[k]
		else:
			r[k] = v
	return r

def toDict(d):
	'''
	convert built-in dict instance to Dict instance
	'''
	D = Dict()
	for k,v in d.iteritems():
		D[k] = toDict(v) if isinstance(v,dict) else v
	return D


configs = config_default.configs
try:
	import config_override
	configs = merge(configs, config_override.configs)
except ImportError:
	pass

configs = toDict(configs)
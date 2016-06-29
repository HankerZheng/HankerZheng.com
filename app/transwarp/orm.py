#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Database operation module. This module is independent with web module.
'''

import time, logging
import db

class Field(object):
	'''
	the basic class for a field
	define the property of one field
	'''
	_count = 0

	def __init__(self, **kw):
		self.name = kw.get('name', None)
		self._default = kw.get('default', None)
		self.primary_key = kw.get('primary_key', False)
		self.nullable = kw.get('nullable', False)
		self.updatable = kw.get('updatable', True)
		self.insertable = kw.get('insertable', True)
		self.ddl = kw.get('ddl','')
		self._order = Field._count
		Field._count += 1

	@property
	def default(self):
		d = self._default
		return d() if callable(d) else d

	def __str__(self):
		s = ['<%s:%s,%s,default(%s),' % (self.__class__.__name__, self.name, self.ddl, self._default)]
		self.nullable and s.append('N')
		self.updatable and s.append('U')
		self.insertable and s.append('I')
		s.append('>')
		return ''.join(s)

class StringField(Field):
	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = ''
		if not 'ddl' in kw:
			kw['ddl'] = 'varchar(255)'
		super(StringField, self).__init__(**kw)

class IntegerField(Field):
	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = 0
		if not 'ddl' in kw:
			kw['ddl'] = 'bigint'
		super(IntegerField, self).__init__(**kw)

class FloatField(Field):
	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = 0.0
		if not 'ddl' in kw:
			kw['ddl'] = 'real'
		super(FloatField, self).__init__(**kw)

class BooleanField(Field):
	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = False
		if not 'ddl' in kw:
			kw['ddl'] = 'bool'
		super(BooleanField, self).__init__(**kw)

class TextField(Field):
	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = ''
		if not 'ddl' in kw:
			kw['ddl'] = 'text'
		super(TextField, self).__init__(**kw)

class BlobField(Field):
	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = ''
		if not 'ddl' in kw:
			kw['ddl'] = 'blob'
		super(BlobField, self).__init__(**kw)

class VersionField(Field):
	def __init__(self, name = None):
		super(VersionField, self).__init__(name=name, default=0, ddl='bigint')

_triggers = frozenset(['pre_insert', 'pre_update', 'pre_delete'])

def _gen_sql(table_name, mappings):
	'''
	1. create table table_name
	2. create fields for the table from mappings
	'''
	pk = None
	# -- is a comment char in SQL
	sql = ['-- generating SQL for %s:' % table_name, 'create table `%s` (' % table_name]
	for f in sorted(mappings.values(), lambda x,y: cmp(x._order, y._order)):
		if not hasattr(f, 'ddl'):
			raise StandardError('no ddl in field "%s".' % n)
		ddl = f.ddl
		nullable = f.nullable
		if f.primary_key:
			pk = f.name
		sql.append(nullable and '  `%s` %s,' % (f.name, ddl) or '  `%s` %s not null,' % (f.name, ddl))
	sql.append('  primary key(`%s`)' % pk)
	sql.append(');')
	return '\n'.join(sql)


class ModelMetaclass(type):
	'''
	Metaclass for model objects.
	1. 	create 'subclasses' attrs for each model class
	'''
	def __new__(cls, name, bases, attrs):
	# when name='User', 
	#	attrs= { '__module__': '__main__', 
	#			 'name': <__main__.StringField object at 0x000000000308BBE0>, 
	#			 'passwd': <__main__.StringField object at 0x000000000308BC50>,
	#			 'id': <__main__.IntegerField object at 0x000000000308BB70>, 
	#			 'pre_insert': <function pre_insert at 0x00000000030A3048>, 
	#			 'last_modified': <__main__.FloatField object at 0x000000000308BC88>, 
	#			 'email': <__main__.StringField object at 0x000000000308BC18>}

		# skip base Model class
		# all the classes we want to operate are inhereted from Model
		if name == "Model":
			return type.__new__(cls, name, bases, attrs)

		# store all subclasses info:
		if not hasattr(cls, 'subclasses'):
			cls.subclasses = {}
		if not name in cls.subclasses:
			cls.subclasses[name] = name
		else:
			logging.warning('Redefine class: %s' % name)

		logging.info('Scan ORMapping %s...' % name)
		mappings = dict()
		primary_key = None
		# store each field in mappings
		for k,v in attrs.iteritems():
			# read the attrs of class Field
			if isinstance(v, Field):
				# assign name property of Field
				# (k,v) could be ('created_at', FloatField), ('title', StringField) for Blog
				if not v.name:
					v.name = k
				logging.info('Found mapping: %s => %s' % (k,v))
				# search for 'primary_key' 
				if v.primary_key:
					# check duplicate primary key
					if primary_key:
						raise TypeError('Cannot define more than 1 primary key in class: %s' % name)
					if v.updatable:
						logging.warning('NOTE: change primary key to non-updatable.')
						v.updatable = False
					if v.nullable:
						logging.warning('NOTE: change primary key to non-nullable.')
						v.nullable = False
					primary_key = v
				# store information in mappings dictionary
				# `mappings` could be {'created_at': FloatField, 'title': StringField} 
				mappings[k] = v
		# check exist of primary key:
		if not primary_key:
			raise TypeError('Primary key not defined in class: %s' % name)
		# delete all the attrs that is an instance of class Field
		for k in mappings.iterkeys():
			attrs.pop(k)
		# create __table__ property to class, `name` here could be blogs, photos, users and so on
		if not '__table__' in attrs:
			attrs['__table__'] = name.lower()

		# create __mapping__ property to class
		# which store all the attr deleted in `pop()`
		attrs['__mapping__'] = mappings
		# create __primary_key__ property to class
		attrs['__primary_key__'] = primary_key
		# create __sql__ property to class for table-generating SQL script
		attrs['__sql__'] = lambda self: _gen_sql(attrs['__table__'], mappings)
		# create 'pre_insert', 'pre_update', 'pre_delete' properties to class
		# if not mentioned, set them to None so that `attrs['pre_update']` won't raise KeyError
		for triggers in _triggers:
			if triggers not in attrs:
				attrs[triggers] = None
		return type.__new__(cls, name, bases, attrs)


class Model(dict):
	'''
	Base class for ORM.
	Define different methods of MySQL for Model

	>>> class User(Model):
	... 	id = IntegerField(primary_key=True)
	... 	name = StringField()
	... 	email = StringField(updatable = False)
	... 	passwd = StringField(default = lambda: '******')
	... 	last_modified = FloatField()
	... 	def pre_insert(self):
	... 		self.last_modified = time.time()
	>>> u = User(id=10190, name='Han', email='jjkk@163.com')
	>>> r = u.insert()
	>>> u.email
	'jjkk@163.com'
	>>> u.passwd
	'******'
	>>> u.last_modified > (time.time() - 2)
	True
	>>> f = User.get(10190)
	>>> f.name
	u'Han'
	>>> f.email
	u'jjkk@163.com'
	>>> f.email = 'changed@163.com'
	>>> r = f.update()   # change email but email is non-updatable!
	>>> len(User.find_all())
	1
	>>> g = User.get(10190)
	>>> g.email
	u'jjkk@163.com'
	>>> r = g.delete()
	>>> len(db.select('select * from user where id=10190'))
	0
	>>> import json
	>>> print User().__sql__()
	-- generating SQL for user:
	create table `user` (
	  `id` bigint not null,
	  `name` varchar(255) not null,
	  `email` varchar(255) not null,
	  `passwd` varchar(255) not null,
	  `last_modified` real not null,
	  primary key(`id`)
	);
	'''

	__metaclass__ = ModelMetaclass

	def __init__(self, **kw):
		super(Model, self).__init__(**kw)

	def __getattr__(self, key):
		try:
			return self[key]
		except:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

	@classmethod
	def get(cls,pk):
		'''
		get by primary key.
		return a dict containing the data we need
		'''
		d = db.select_one('select * from %s where %s=?' % (cls.__table__, cls.__primary_key__.name), pk)
		return cls(**d) if d else None

	@classmethod
	def find_first(cls, where, *args):
		'''
		Find by  where clause and return one result. If multiple results found,
		only the first one returned. If no result found, return None.
		'''
		d = db.select_one('select * from %s %s' % (cls.__table__, where), *args)
		return cls(**d) if d else None

	@classmethod
	def find_all(cls, *args):
		'''
		Find by where clause and return list
		'''
		L = db.select('select * from `%s`' % cls.__table__)
		return [cls(**d) for d in L]

	@classmethod
	def find_by(cls, where, *args):
		'''
		FInd by where clause and return list.
		'''
		L = db.select('select * from `%s` %s' % (cls.__table__, where), *args)
		return [cls(**d) for d in L]

	@classmethod
	def count_all(cls):
		'''
		Find by 'select count(pk) from table' and return integer.
		'''
		return db.select_int('select count(`%s`) from `%s`' % (cls.__primary_key__.name, cls.__table__))

	@classmethod
	def count_by(cls, where, *args):
		'''
		Find by 'select count(pk) from table where ...' and return int
		'''
		return db.select_int('select count(`%s`) from `%s` %s' % (cls.__primary_key__.name, cls.__table__, where))

	def update(self):
		self.pre_update and self.pre_update()
		L = []
		args = []
		for k,v in self.__mapping__.iteritems():
			if v.updatable:
				if hasattr(self,k):
					arg = getattr(self,k)
				else:
					arg = v.default
					setattr(self, k, arg)
				L.append('`%s`=?' % k)
				args.append(arg)
		pk = self.__primary_key__.name
		args.append(getattr(self,pk))
		db.update('update `%s` set %s where %s=?' % (self.__table__, ','.join(L), pk), *args)
		return self

	def delete(self):
		self.pre_delete and self.pre_delete()
		pk = self.__primary_key__.name
		args = (getattr(self,pk), )
		db.update('delete from `%s` where `%s`=?' % (self.__table__, pk), *args)
		return self

	def insert(self):
		self.pre_insert and self.pre_insert()
		params = {}
		for k,v in self.__mapping__.iteritems():
			if v.insertable:
				if not hasattr(self,k):
					setattr(self,k,v.default)
				params[v.name] = getattr(self, k)
		db.insert('%s' % self.__table__, **params)
		return self

if __name__ == '__main__':
	logging.basicConfig(level = logging.DEBUG)
	db.create_engine(user='myblogbytranswarp', password='ThisIsPassWord', database='test')
	db.update('drop table if exists user')
	db.update('create table user (id int primary key, name text, email text, passwd text, last_modified real)')
	import doctest
	doctest.testmod()
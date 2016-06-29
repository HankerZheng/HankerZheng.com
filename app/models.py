#!/user/bin/env python
# -*- coding: utf-8 -*-


'''
Models for user, blog, comment.
'''

import time, uuid

from transwarp.db import next_id
from transwarp.orm import Model, StringField, BooleanField, FloatField, TextField, BlobField, IntegerField, Field

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
	__table__ = 'users'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	password = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	created_at = FloatField(updatable=False, default=time.time)

class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	title = StringField(ddl='varchar(50)')
	tags = StringField(ddl='varchar(100)')
	summary = StringField(ddl='varchar(200)')	
	content = TextField(ddl='mediumtext')
	cr_year = IntegerField(ddl='smallint')
	cr_month = IntegerField(ddl='tinyint')
	created_at = FloatField(updatable=False, default=time.time)

class Photo(Model):
	__table__ = 'photos'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	title = StringField(ddl='varchar(50)')
	descript = StringField(ddl='varchar(200)')
	path = StringField(ddl='varchar(100)')
	loc_name = StringField(ddl='varchar(50)')
	loc_lat = FloatField(ddl='float(10,6)')
	loc_lng = FloatField(ddl='float(10,6)')
	created_at = FloatField(updatable=False, default=time.time)

class Tag(Model):
	__table__ = 'tags'

	tag_name = StringField(primary_key=True, ddl='varchar(50)')
	blogs = TextField(ddl='text')
	count = IntegerField(ddl='smallint')
	created_at = FloatField(updatable=False, default=time.time)


if __name__ == "__main__":
	print User().__sql__()
	print Blog().__sql__()
	print Photo().__sql__()
	print Tag().__sql__()
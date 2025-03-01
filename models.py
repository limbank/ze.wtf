from peewee import *

db = SqliteDatabase('short.db')

class Invites(Model):
  invites_id = IntegerField(primary_key=True)
  created_by = IntegerField()
  used_by = IntegerField()
  created = DateTimeField()
  expires = DateTimeField()
  code = CharField()

  class Meta:
    database = db
    db_table = 'invites'

class Cookie(Model):
  cookies_id = IntegerField(primary_key=True)
  user_id = IntegerField()
  created = DateTimeField()
  expires = DateTimeField()
  cookie_token = CharField()
  cookie_hash = CharField()

  class Meta:
    database = db
    db_table = 'cookies'

class User(Model):
  users_id = IntegerField(primary_key=True)
  date_joined = DateTimeField()
  username = CharField(unique=True)
  email = CharField()
  password = CharField()

  class Meta:
    database = db
    db_table = 'users'

class Link(Model):
  links_id = IntegerField(primary_key=True)
  date_created = DateTimeField()
  url = CharField()
  ref = CharField(unique=True)
  owner = IntegerField(default=0)
  visits = IntegerField(default=0)

  class Meta:
    database = db
    db_table = 'links'

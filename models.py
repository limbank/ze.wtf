from peewee import *

db = SqliteDatabase('short.db')

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

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

class Invites(Model):
  invites_id = IntegerField(primary_key=True)
  created_by = ForeignKeyField(User, backref='created_invites', on_delete='CASCADE', column_name='created_by')  
  used_by = ForeignKeyField(User, backref='used_invites', null=True, on_delete='SET NULL', column_name='used_by')
  created = DateTimeField()
  expires = DateTimeField()
  code = CharField()

  class Meta:
    database = db
    db_table = 'invites'

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

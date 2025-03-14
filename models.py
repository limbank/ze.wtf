import os
from datetime import datetime
from dotenv import load_dotenv
from peewee import *

load_dotenv()

db = PostgresqlDatabase(os.getenv('DB_NAME'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'))

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
  role = IntegerField()

  class Meta:
    database = db
    db_table = 'users'

class File(Model):
  files_id = IntegerField(primary_key=True)
  owner = IntegerField()
  created = DateTimeField()
  filename = CharField(unique=True)
  location = CharField()
  original = CharField()

  class Meta:
    database = db
    db_table = 'files'

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

class Role(Model):
  roles_id = AutoField(primary_key=True)
  name = CharField()

  class Meta:
    database = db
    db_table = 'roles'

class Permission(Model):
  permissions_id = AutoField(primary_key=True)
  name = CharField()

  class Meta:
    database = db
    db_table = 'permissions'

class RolePerm(Model):
  roleperms_id = AutoField(primary_key=True)
  role_id = ForeignKeyField(Role, backref='permissions', column_name='role_id')  
  perm_id = ForeignKeyField(Permission, backref='roles', column_name='perm_id')

  class Meta:
    database = db
    db_table = 'roleperms'

class Space(Model):
  spaces_id = AutoField(primary_key=True)
  name = CharField()
  owner = ForeignKeyField(User, backref='spaces')
  date_created = DateTimeField(default=datetime.now)

  class Meta:
    database = db
    db_table = 'spaces'

db.connect()
#db.create_tables([Link, Invites, File, User, Cookie, Role, Permission, RolePerm])

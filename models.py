import os
from datetime import datetime
from dotenv import load_dotenv
from peewee import *

load_dotenv()

db = PostgresqlDatabase(os.getenv('DB_NAME'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'))

class Cookie(Model):
  cookies_id = IntegerField(primary_key=True)
  user_id = IntegerField()
  created = DateTimeField(default=datetime.now)
  expires = DateTimeField()
  cookie_token = CharField()
  cookie_hash = CharField()

  class Meta:
    database = db
    db_table = 'cookies'

class User(Model):
  users_id = IntegerField(primary_key=True)
  date_joined = DateTimeField(default=datetime.now)
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
  created = DateTimeField(default=datetime.now)
  filename = CharField(unique=True)
  location = CharField()
  original = CharField()

  class Meta:
    database = db
    db_table = 'files'

class Invite(Model):
  invites_id = IntegerField(primary_key=True)
  created_by = ForeignKeyField(User, backref='created_invites', column_name='created_by')  
  used_by = ForeignKeyField(User, backref='used_invites', null=True, column_name='used_by')
  created = DateTimeField(default=datetime.now)
  expires = DateTimeField(null=True)
  code = CharField()

  class Meta:
    database = db
    db_table = 'invites'

  def is_expired(self):
    if self.expires is None:
      return False  # Never expires
    return datetime.now() > self.expires

class Link(Model):
  links_id = IntegerField(primary_key=True)
  date_created = DateTimeField(default=datetime.now)
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

class Key(Model):
  keys_id = AutoField(primary_key=True)
  value = CharField()
  name = CharField()
  owner = ForeignKeyField(User, backref='keys')
  date_created = DateTimeField(default=datetime.now)
  expires = DateTimeField(null=True)

  class Meta:
    database = db
    db_table = 'keys'

  def is_expired(self):
    if self.expires is None:
      return False  # Never expires
    return datetime.now() > self.expires

class Blot(Model):
  blots_id = AutoField(primary_key=True)
  message = CharField()
  date_created = DateTimeField(default=datetime.now)
  date_expires = DateTimeField(null=True)

  class Meta:
    database = db
    db_table = 'blots'

class AccessLog(Model):
  accesslogs_id = AutoField(primary_key=True)
  ip_address = CharField()
  user_agent = CharField()
  route = CharField()
  domain = CharField()
  date_created = DateTimeField(default=datetime.now)

  class Meta:
    database = db
    db_table = 'accesslog'

def create_tables():
  with db:
    db.create_tables([Link, Invite, File, User, Cookie, Role, Permission, RolePerm, Space, Key, Blot, AccessLog], safe=True)
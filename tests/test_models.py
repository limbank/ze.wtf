import os
import unittest

import psycopg2
from peewee import PostgresqlDatabase
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from models import Link, Invite, File, User, Cookie, Role, Permission, RolePerm, Space, Key

MODELS = [Link, Invite, File, User, Cookie, Role, Permission, RolePerm, Space, Key]

test_db = PostgresqlDatabase(None)

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Creates und initializes the test database before running tests."""
        cls.create_test_database()

        test_db_name = (os.getenv('DB_NAME') or 'sqlite') + '_test'

        test_db.init(
            test_db_name,
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
        )

    @classmethod
    def tearDownClass(cls):
        """Drops the test database after tests are complete."""
        cls.drop_test_database()

    def setUp(self):
        self.create_test_database()
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since postgres test db only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

    def test_empty_db(self):
        # Note: yes we can simplify this test and use a for loop, but I don't care lol

        # Arrange
        link_count = Link.select().count()
        invite_count = Invite.select().count()
        file_count = File.select().count()
        user_count = User.select().count()
        cookie_count = Cookie.select().count()
        role_count = Role.select().count()
        permission_count = Permission.select().count()
        role_perm_count = RolePerm.select().count()
        space_count = Space.select().count()
        key_count = Key.select().count()

        # Assert
        self.assertEqual(link_count, 0, f"Expected 0 links in the database, but found {link_count}.")
        self.assertEqual(invite_count, 0, f"Expected 0 invites in the database, but found {invite_count}.")
        self.assertEqual(file_count, 0, f"Expected 0 files in the database, but found {file_count}.")
        self.assertEqual(user_count, 0, f"Expected 0 users in the database, but found {user_count}.")
        self.assertEqual(cookie_count, 0, f"Expected 0 cookies in the database, but found {cookie_count}.")
        self.assertEqual(role_count, 0, f"Expected 0 roles in the database, but found {role_count}.")
        self.assertEqual(permission_count, 0, f"Expected 0 permissions in the database, but found {permission_count}.")
        self.assertEqual(role_perm_count, 0, f"Expected 0 role perms in the database, but found {role_perm_count}.")
        self.assertEqual(space_count, 0, f"Expected 0 spaces in the database, but found {space_count}.")
        self.assertEqual(key_count, 0, f"Expected 0 keys in the database, but found {key_count}.")

    @staticmethod
    def create_test_database():
        """
        Creates the test database if it doesn't exist.

        Refs:
            1. https://www.geeksforgeeks.org/python-postgresql-create-database/
            2. https://stackoverflow.com/questions/34484066/create-a-postgres-database-using-python
            3. https://mljar.com/notebooks/postgresql-python-drop-table/
        """
        con = psycopg2.connect(
            dbname='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cur = con.cursor()

        test_db_name = (os.getenv('DB_NAME') or 'sqlite') + '_test'

        cur.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(sql.Literal(test_db_name))
        )
        exists = cur.fetchone()

        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(test_db_name)))

        # Closing the connection
        cur.close()
        con.close()

    @staticmethod
    def drop_test_database():
        """
        Drops the test database after tests are complete.

        Refs:
            1. https://www.geeksforgeeks.org/python-postgresql-create-database/
            2. https://stackoverflow.com/questions/34484066/create-a-postgres-database-using-python
            3. https://mljar.com/notebooks/postgresql-python-drop-table/
        """
        con = psycopg2.connect(
            dbname='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cur = con.cursor()

        test_db_name = (os.getenv('DB_NAME') or 'sqlite') + '_test'

        # Use the psycopg2.sql module instead of string concatenation
        # in order to avoid sql injection attacks.
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
            sql.Identifier(test_db_name))
        )

        # Closing the connection
        cur.close()
        con.close()

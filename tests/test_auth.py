import os
import unittest

import psycopg2
from peewee import PostgresqlDatabase
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from models import Link, Invite, File, User, Cookie, Role, Permission, RolePerm, Space, Key
from zewtf import app

MODELS = [Link, Invite, File, User, Cookie, Role, Permission, RolePerm, Space, Key]

test_db = PostgresqlDatabase(None)

class AuthTestCase(unittest.TestCase):
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

        # Override DB_NAME environment variable
        os.environ["DB_NAME"] = "test_db_name"  # Forces models.py to use `{os.getenv('DB_NAME')}_test`

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

        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        # Not strictly necessary since postgres test db only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        self.ctx.pop()

    def test_home(self):
        response = self.client.post("/", data={"content": "hello world"})
        assert response.status_code == 200
        assert "POST method called" == response.get_data(as_text=True)

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

import os
import unittest

import psycopg2
from peewee import PostgresqlDatabase
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

MODELS = []

# use an in-memory SQLite for tests.
test_db = PostgresqlDatabase(None)

class BaseTestCase(unittest.TestCase):


    def setUp(self):
        self.create_test_database()
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        self.drop_test_database()

    def create_test_database(self):
        """
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
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(test_db_name))
        )

        # Closing the connection
        cur.close()
        con.close()

    def drop_test_database(self):
        """
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
        cur.execute(sql.SQL("DROP DATABASE {}").format(
            sql.Identifier(test_db_name))
        )

        # Closing the connection
        cur.close()
        con.close()

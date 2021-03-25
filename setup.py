#!/usr/bin/env python

from distutils.core import setup

setup(
    name='dbconnect',
    version='0.0.1',
    packages=['dbconnect'],
    install_requires=["psycopg2-binary", "pymysql", "sqlalchemy", "boto3", "awscli", "sqlalchemy-redshift"]
)

"""Easily create connections to our databases by using your AWS credentials."""
import os
import webbrowser
import boto3
from sqlalchemy import create_engine
from urllib.parse import quote_plus

SSM = boto3.client('ssm')


def get_databases():
    """Return the database names that can be connected to."""
    return _get_param("/dbconnect/dbnames").split(',')


def create_connection(**kwargs):
    """Return a SQLAlchemy connection to the database specified."""
    database = kwargs['database']

    def get_database_param(param):
        env_variable = "DBCONNECT_{param_upper}".format(param_upper=param.upper())
        if env_variable in os.environ:
            return os.environ[env_variable]
        return _get_param("/dbconnect/{database}/{param}".format(database=database, param=param))

    prefix = _get_db_prefix(database)
    if "awsathena" in prefix:
        connection_string = "{prefix}://{user}:{password}@{endpoint}:{port}/{database}?s3_staging_dir={s3_staging_dir}".format(
            prefix=prefix,
            user=quote_plus(get_database_param("user")),
            password=quote_plus(get_database_param("password")),
            endpoint=quote_plus(get_database_param("endpoint")),
            port=quote_plus(get_database_param("port")),
            database=quote_plus("main-app"),
            s3_staging_dir=quote_plus(get_database_param("s3-staging")))
    else:
        connection_string = "{prefix}://{user}:{password}@{endpoint}:{port}/{database}".format(
            prefix=prefix,
            user=get_database_param("user"),
            password=get_database_param("password"),
            endpoint=get_database_param("endpoint"),
            port=get_database_param("port"),
            database=get_database_param("database"))

    if "localhost" in connection_string:
        return create_engine(connection_string, connect_args={'sslmode': 'verify-ca'})

    return create_engine(connection_string)


def get_docs(**kwargs):
    """Open the database documentation of the database specified."""
    url = _get_param("/dbconnect/{database}/docs".format(database=kwargs['database']))
    print("Opening \"{url}\"".format(url=url))
    webbrowser.open(url)


def _get_param(endpoint):
    response = SSM.get_parameter(
        Name=endpoint,
        WithDecryption=True
    )
    return response['Parameter']['Value']


def _get_db_prefix(database):
    db_type = _get_param("/dbconnect/{database}/type".format(database=database))
    if db_type == 'mysql':
        return 'mysql+pymysql'
    elif db_type == 'postgresql':
        return 'postgresql'
    elif db_type == 'awsathena':
        return 'awsathena+jdbc'
    elif db_type == 'redshift':
        return 'redshift+psycopg2'

"""Easily create connections to our databases by using your AWS credentials."""
import webbrowser
import boto3
from sqlalchemy import create_engine
from urllib.parse import quote_plus

SSM = boto3.client('ssm')
STS = boto3.client('sts')
RED = boto3.client('redshift')

def get_databases():
    """Return the database names that can be connected to."""
    return _get_param("/dbconnect/dbnames").split(',')


def create_connection(**kwargs):
    """Return a SQLAlchemy connection to the database specified."""
    database = kwargs['database']

    prefix = _get_db_prefix(database)
    if "awsathena" in prefix:
        connection_string = "{prefix}://{user}:{password}@{endpoint}:{port}/{database}?s3_staging_dir={s3_staging_dir}".format(
            prefix=prefix,
            user=quote_plus(_get_param("/dbconnect/{database}/user".format(database=database))),
            password=quote_plus(_get_param("/dbconnect/{database}/password".format(database=database))),
            endpoint=quote_plus(_get_param("/dbconnect/{database}/endpoint".format(database=database))),
            port=quote_plus(_get_param("/dbconnect/{database}/port".format(database=database))),
            database=quote_plus("main-app"),
            s3_staging_dir=quote_plus(_get_param("/dbconnect/{database}/s3-staging".format(database=database))))
    elif "redshift" in prefix:
        creds = _get_redshift_creds(database)
        connection_string = "{prefix}://{user}:{password}@{endpoint}:{port}/{database}".format(
            prefix=prefix,
            user=quote_plus(creds['DbUser']),
            password=creds['DbPassword'],
            endpoint=_get_param("/dbconnect/{database}/endpoint".format(database=database)),
            port=_get_param("/dbconnect/{database}/port".format(database=database)),
            database=_get_param("/dbconnect/{database}/database".format(database=database)))
    else:
        connection_string = "{prefix}://{user}:{password}@{endpoint}:{port}/{database}".format(
            prefix=prefix,
            user=_get_param("/dbconnect/{database}/user".format(database=database)),
            password=_get_param("/dbconnect/{database}/password".format(database=database)),
            endpoint=_get_param("/dbconnect/{database}/endpoint".format(database=database)),
            port=_get_param("/dbconnect/{database}/port".format(database=database)),
            database=_get_param("/dbconnect/{database}/database".format(database=database)))

    return create_engine(connection_string)


def get_docs(**kwargs):
    """Open the database documentation of the database specified."""
    url = _get_param("/dbconnect/{database}/docs".format(database=kwargs['database']))
    print("Opening \"{url}\"".format(url=url))
    webbrowser.open(url)


def _get_redshift_creds(database):
    ident = STS.get_caller_identity()
    username = ident['UserId'].split(':')[1]

    import datetime

    print(datetime.datetime.now())
    dbuser = RED.get_cluster_credentials(
            DbUser=username,
            ClusterIdentifier=_get_param("/dbconnect/{database}/endpoint".format(database=database)).split('.').pop(0),
            AutoCreate=True,
            DbGroups=[
                'iam',
                'readonlyusers'
            ]
    )
    print(datetime.datetime.now())
    return dbuser

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

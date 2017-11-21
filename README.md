# DBConnect

### Why use this module?
- Make it easy to discover new databases at DataCamp
- Allow us to rotate DB credentials, without anyone having to update their scripts
- Make it easy to open the documentation of a database
- Allow fine-grained access permissions by using the AWS Key and Secrets for each client.

## Installation
Make sure to ask the IDE team for your AWS Key and Secret.
```bash
pip install awscli

aws configure
> AWS Access Key ID: <enter your key>
> AWS Secret Access Key: <enter your secret>
> Default region name: us-east-1
> Default output format: <leave blank>

pip install git+https://github.com/datacamp/dbconnect-python
```

## How to use
**For security reasons, we only allow DB connections from our VPN. Make sure to be connected when using this module.**

Get a list of our databases you can connect to:
```python
import dbconnect as dbc
dbc.get_databases()
['main-app',
 'teach-app',
 'challenges-app',
 'projects-app',
 'mobile-app',
 'messenger-app',
 'projector-app',
 'datachats',
 'timetracker']
```

Connect to a database and execute pandas queries:
```python
import dbconnect as dbc
import pandas as pd

engine = dbc.create_connection(database = 'main-app') # The 'main-app' string you can find from dbc.get_databases()
pd.read_sql('SELECT id, email FROM users ORDER BY id ASC LIMIT 10', engine)
```

Open the documentation of a database
```python
dbc.get_docs(database="main-app")
Opening "https://github.com/datacamp/main-app/wiki/Database-Documentation"
```

## AWS Parameter Store Structure
| Parameter | Value |
| --------- | ----- |
| /dbconnect/dbnames | List of `<application-name>`s, separated with comma. |

For every application:

| Parameter | Value |
| --------- | ----- |
| `/dbconnect/<application-name>/type` | Type of database (mysql, postgresql) |
| `/dbconnect/<application-name>/endpoint` | Endpoint of the replica |
| `/dbconnect/<application-name>/port` | Port of the replica |
| `/dbconnect/<application-name>/user` | Username of the connection |
| `/dbconnect/<application-name>/database` | Name of the database |
| `/dbconnect/<application-name>/docs` | URL of the database documentation |
| `/dbconnect/<application-name>/password` | Password of the database. **Make sure the `type` is set to `SecureString`** |

These paramters are managed by terraform. (Ask the IDE team)
#
# Add new users in the 
# PixelTailor database.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: final_adduser**")
    
    #
    # setup AWS based on config file:
    #
    #TODO: config file needed
    #
    config_file = '####'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')

    # Access request body
    print("**Accessing request body**")
    if "body" not in event:
        raise Exception("event has no body")

    body = json.loads(event["body"])  

    if "username" not in body:
        raise Exception("Username is required.")
    if "password" not in body:
        raise Exception("Password is required.")
    if "bucketfolder" not in body:
        raise Exception("Bucketfolder is required.")

    username = body["username"]
    password = body["password"]
    bucketfolder =body["bucketfolder"]

    print("Username:", username)
    print("Password:", password)

    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    # Insert the new user into the database
    print("**Adding user to database**")
    sql = """
        INSERT INTO users(username, password, bucketfolder)
        VALUES(%s, %s, %s);
    """
    datatier.perform_action(dbConn, sql, [username, password, bucketfolder])

    # Retrieve the user ID of the newly added user
    sql = "SELECT LAST_INSERT_ID();"
    row = datatier.retrieve_one_row(dbConn, sql)
    userid = row[0]

    print("UserID:", userid)

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, new user added**")
    
    return {
      'statusCode': 200,
      'body': json.dumps({"message": "User added successfully.", "userId": userid})
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }

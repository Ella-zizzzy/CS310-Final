#
# Retrieves and returns all the lables  
# of the user with the input user id
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING LABEL RETRIEVAL**")
    print("**lambda: retrieve_lables**")
    
    #
    # setup AWS based on config file:
    #TO DO: name of the config
    config_file = 'NAME-config.ini'
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

    #
    # userid from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
    #
    print("**Accessing event/pathParameters**")
    
    if "userid" in event:
      userid = event["userid"]
    elif "pathParameters" in event:
      if "userid" in event["pathParameters"]:
        userid = event["pathParameters"]["userid"]
      else:
        raise Exception("requires userid parameter in pathParameters")
    else:
        raise Exception("requires userid parameter in event")
        
    print("userid:", userid)



    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # now retrieve lables by the input user id:
    #
    print("**Retrieving data**")

    #
    # write sql query to select all lables (unique) from Lable with userid
    #
    sql_get_lables = "SELECT DISTINCT lablename FROM Lable WHERE userid = %s ORDER BY lablename;"
    
    lables = datatier.retrieve_all_rows(dbConn, sql_get_lables,(userid,))


    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #

    #if no lables found
    if not lables:
      return{
        'statusCode': 400;
        'body': json.dunps({"message": f"No labels found for the user {userid}"})
      }

    # found successfully and display lables of userid #
    
    print("**DONE, lables found successfully**")

    label_list = [label[0] for label in labels]

    return{
      'statusCode': 200;
      'body': json.dunps(label_list)
    }


  except Exception as err:
    print("**ERROR retrieving labels**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps({"error": str(err)})
    }

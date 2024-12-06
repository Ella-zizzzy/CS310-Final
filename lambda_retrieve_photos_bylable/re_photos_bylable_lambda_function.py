#
# Retrieves and returns all the photos of user with the input lable
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj03_users**")
    
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
    ##if the cilent use other name of lables MODIFY selected_lable
    if "selected_lable" in event:
      selected_lable = event["selected_lable"]
    elif "pathParameters" in event:
      if "selected_lable" in event["pathParameters"]:
        selected_lable = event["pathParameters"]["selected_lable"]
      else:
        raise Exception("requires selected_lable parameter in pathParameters")
    else:
        raise Exception("requires selected_lable parameter in event")
        
    print("selected_lable:", selected_lable)

    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # now retrieve all the photo by the input user id an lable:
    #
    print("**Retrieving data**")

    #
    # write sql query to select all photos from the Photos table
    #
    sql_get_photos =  """
        SELECT p.photoid, 
               p.original_name, 
               p.bucketkey, 
               l.labelname, 
        FROM Photos p
        JOIN Label l ON p.photoid = l.photoid AND p.userid = l.userid
        WHERE p.userid = %s AND l.labelname = %s
        """
    
    photos = datatier.retrieve_all_rows(dbConn, sql_get_photos, (userid, selected_lable))

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #

    #if no photos found
    if not photos:
      return {
        'statusCode': 400,
        'body': json.dumps({"message": f"No photos found for user {userid} with label {selected_lable}"})
      }

    # found successfully and display photos with lable of userid #
    
    print("**DONE, photos found successfully**")
    
    photo_list = []
    for photo in photos:
      photo_list.append({
        'userid' : userid,
        'photoid': photo[0],
        'labelname': photo[3],
        'original_name': photo[1],
        'bucketkey': photo[2]
        
      })

    #return successful response
    return {
      'statusCode': 200,
      'body': json.dumps(photo_list)
    }
    
  except Exception as err:
    print("**ERROR retrieveing phhotos**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps({"error": str(err)})
    }

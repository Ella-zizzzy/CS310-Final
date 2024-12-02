import json
import boto3
import os
import datatier
from configparser import ConfigParser

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: final_delete_image**")

        # Setup AWS based on config file
        config_file = '#####'  
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        #
        # configure for S3 access:
        #
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)
        
        bucketname = configur.get('s3', 'bucket_name')
        
        s3 = boto3.resource('s3')
        
        # Configure for RDS access
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        # Access userid from event
        print("**Accessing event/pathParameters**")
        if "userid" in event:
            userid = event["userid"]
        elif "pathParameters" in event and "userid" in event["pathParameters"]:
            userid = event["pathParameters"]["userid"]
        else:
            raise Exception("requires userid parameter in event or pathParameters")

        print("userid:", userid)

        # Access photoid from request body
        print("**Accessing request body**")
        if "body" not in event:
            raise Exception("event has no body")

        body = json.loads(event["body"])  # Parse the JSON

        if "photoid" not in body:
            raise Exception("event body missing 'photoid'")

        photoid = body["photoid"]
        print("photoid:", photoid)

        # Open connection to the database
        print("**Opening database connection**")
        dbConn = datatier.get_dbConn(
            rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname
        )

        # Check if userid is valid
        print("**Checking if userid is valid**")
        sql = "SELECT * FROM users WHERE userid = %s;"
        user_row = datatier.retrieve_one_row(dbConn, sql, [userid])

        if not user_row:
            print("**No such user, returning...**")
            return {
                'statusCode': 400,
                'body': json.dumps("No such user.")
            }

        # Check if photo exists and belongs to the user
        print("**Checking if photo exists and belongs to the user**")
        sql = "SELECT photoid, bucketkey FROM photos WHERE photoid = %s AND userid = %s;"
        asset_row = datatier.retrieve_one_row(dbConn, sql, [photoid, userid])

        if not asset_row:
            print("**Photo not found or does not belong to user**")
            return {
                'statusCode': 400,
                'body': json.dumps("Photo not found or does not belong to user.")
            }

        bucketkey = asset_row[1]
        print("datafilekey:", bucketkey)

        # Delete the photo from S3
        print("**Deleting photo from S3**")
        s3_object = s3.Object(bucketname, bucketkey)
        s3_object.delete()

        # Delete the photo's metadata from the database
        print("**Deleting photo's metadata from database**")
        sql = "DELETE FROM photos WHERE photoid = %s AND userid = %s;"
        datatier.perform_action(dbConn, sql, [photoid, userid])

        # Close the database connection
        dbConn.close()

        # Respond with success
        print("**DONE, photo deleted**")
        return {
            'statusCode': 200,
            'body': json.dumps("Photo deleted successfully.")
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }

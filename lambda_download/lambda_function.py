import boto3
import os
import base64
import datatier
import json  # Input JSON module
from mimetypes import guess_type
from configparser import ConfigParser
import uuid  # For generating unique filenames


def lambda_handler(event, context):
    try:
        print("**STARTING Lambda Function**")
        
        # Setup AWS based on config file
        config_file = 'final-project-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        
        configur = ConfigParser()
        configur.read(config_file)
        
        # Configure S3 access
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)
        
        bucketname = configur.get('s3', 'bucket_name')
        s3_client = boto3.client('s3')  # S3 客户端
        
        # Configure RDS access
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')
        
        # Extract input parameters from API Gateway pathParameters
        path_params = event.get("pathParameters", {})
        userid = path_params.get("userid")
        photoid = path_params.get("photoid")
        
        if not userid or not photoid:
            raise ValueError("Missing required path parameters: 'userid' or 'photoid'")
        
        print(f"User ID: {userid}, Photo ID: {photoid}")
        
        # Open database connection
        print("**Opening connection to RDS**")
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
        
        try:
            # Validate photo ID and user ID
            print("**Verifying Photo ID and User ID**")
            sql_check_job = """
                SELECT bucketkey, original_name 
                FROM photos 
                WHERE photoid = %s AND userid = %s;
            """
            row = datatier.retrieve_one_row(dbConn, sql_check_job, [photoid, userid])
            
            if not row or row == ():
                raise ValueError(f"Photo ID {photoid} does not exist or does not belong to User ID {userid}")
            
            bucketkey, original_name = row
            print(f"Retrieved Bucket Key: {bucketkey}, Original Name: {original_name}")

            # Validate file extension
            allowed_extensions = ['jpg', 'jpeg', 'png']
            file_extension = os.path.splitext(original_name)[1][1:].lower()

            if file_extension not in allowed_extensions:
                raise ValueError(f"Unsupported file type: {file_extension}. Only {allowed_extensions} are allowed.")
            
            # Generate a unique filename using UUID
            unique_filename = f"{uuid.uuid4().hex}_{os.path.basename(original_name)}"
            local_filename = f"/tmp/{unique_filename}"
            
            # Download file from S3
            print("**Downloading File from S3**")
            s3_client.download_file(Bucket=bucketname, Key=bucketkey, Filename=local_filename)
            
            print(f"File downloaded to: {local_filename}")
            
            # Read file and encode as base64
            print("**Reading and Encoding File**")
            with open(local_filename, "rb") as file:
                file_data = file.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')

            # Determine MIME type
            mime_type = guess_type(original_name)[0] or "application/octet-stream"
            
            # Return results
            print("**Returning Results**")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": mime_type},
                "body": json.dumps({
                    "message": "File successfully retrieved",
                    "filename": unique_filename,
                    "encoded_file": encoded_data
                })
            }
        
        finally:
            dbConn.close()
            print("**Database connection closed**")
    
    except ValueError as ve:
        print(f"**INPUT ERROR**: {str(ve)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Bad Request", "error": str(ve)})
        }
    
    except Exception as e:
        print(f"**ERROR**: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }

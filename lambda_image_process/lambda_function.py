from PIL import Image, ImageOps, ImageEnhance
import boto3
import io
import os
import json
import base64
import datatier
from configparser import ConfigParser
import uuid


def lambda_handler(event, context):
    try:
        print("**STARTING IMAGE PROCESSING AND DOWNLOAD**")

        # 1. Setup AWS credentials and config file
        config_file = 'final-project-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        # Configure S3
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)
        bucket_name = configur.get('s3', 'bucket_name')
        s3 = boto3.client('s3')

        # Configure RDS access
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        # 2. Extract input parameters from pathParameters
        path_params = event.get("pathParameters", {})
        userid = path_params.get("userid")
        photoid = path_params.get("photoid")
        operation = path_params.get("operation")

        if not userid or not photoid or not operation:
            raise ValueError("Missing required path parameters: 'userid', 'photoid', or 'operation'")

        print(f"User ID: {userid}, Photo ID: {photoid}, Operation: {operation}")

        # Extract & validate body parameters
        body = json.loads(event.get("body", "{}"))
        params = body.get("parameters", {})

        print(f"Received parameters: {params}")

        # 3. Open DB connection
        print("**Connecting to RDS Database**")
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        try:
            # Validate photo ID and user ID in DB
            print("**Validating Photo ID and User ID in Database**")
            sql = """
                SELECT bucketkey, original_name
                FROM photos
                WHERE photoid = %s AND userid = %s;
            """
            row = datatier.retrieve_one_row(dbConn, sql, [photoid, userid])

            if not row:
                raise ValueError(f"Photo ID {photoid} does not exist or does not belong to User ID {userid}")

            bucketkey, original_name = row
            print(f"Retrieved Bucket Key: {bucketkey}, Original Name: {original_name}")

            # Step 4. Retrieve photo from S3
            print("Retrieving Image from S3")
            response = s3.get_object(Bucket=bucket_name, Key=bucketkey)
            image_data = response["Body"].read()
            img = Image.open(io.BytesIO(image_data))
            original_format = img.format  # Extract the original format (e.g., JPEG, PNG)

            # Step 5. Apply the specified operation
            print("Applying Image Operation")
            if operation == "crop":
                img = img.crop((int(params["left"]), int(params["top"]), int(params["right"]), int(params["bottom"])))
            elif operation == "thumbnail":
                img.thumbnail((128, 128))  # Fixed thumbnail size
            elif operation == "pad":
                img = ImageOps.pad(img, (int(params["width"]), int(params["height"])))
            elif operation == "adjust_color":
                brightness = float(params.get("brightness", 1.0))
                contrast = float(params.get("contrast", 1.0))
                img = ImageEnhance.Brightness(img).enhance(brightness)
                img = ImageEnhance.Contrast(img).enhance(contrast)
            elif operation == "change_color":
                color_hex = params["color"]
                print(f"Applying color overlay: {color_hex}")
    
                # Ensure the color is in HEX format and convert to RGB
                color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
    
                # Convert original image to RGB if not already in that mode
                if img.mode != "RGB":
                    print(f"Converting image mode from {img.mode} to RGB for compatibility...")
                    img = img.convert("RGB")
    
                # Create an overlay image with the same size and mode as the original image
                overlay = Image.new("RGB", img.size, color_rgb)
                # Blend the two images
                img = Image.blend(img, overlay, alpha=0.5)
            else:
                raise ValueError("Unsupported operation")

            # Ensure compatibility with JPEG if required
            if original_format == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Generate unique filename with the correct extension
            file_extension = original_format.lower()
            unique_filename = f"processed_{photoid}_{uuid.uuid4().hex}.{file_extension}"
            local_filename = f"/tmp/{unique_filename}"

            # Save the image in the original format
            img.save(local_filename, format=original_format)

            # Read file and encode as base64
            print("Encoding Image for Response")
            with open(local_filename, "rb") as file:
                encoded_data = base64.b64encode(file.read()).decode('utf-8')

            print("Image Processing and Return Complete")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": f"image/{file_extension}"},
                "body": json.dumps({
                    "message": f"Image processed successfully",
                    "filename": unique_filename,
                    "encoded_preview": encoded_data
                })
            }

        finally:
            dbConn.close()
            print("Database Connection Closed")

    except ValueError as ve:
        print(f"Input error: {str(ve)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Bad Request", "error": str(ve)})
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }
 
# CS310-Final-Pixel-Tailor

# Intelligent Image Processing and Management Platform
Team members: Ziyue Li, Shuyi Han, Rongwei Peng

## Overview
This platform is an intelligent image processing and management system designed to leverage a serverless architecture powered by AWS services. It provides users with a seamless experience for uploading, processing, recognizing, and retrieving images through advanced technologies. The platform integrates AWS Lambda, S3, Rekognition, and RDS (MySQL) to perform efficient image handling and dynamic gallery retrieval.

## Features

### Client-Side Features:
1. **User Management**:
   - Users can register and manage their image collections.

2. **View Image List**:
   - View all uploaded images associated with their account.

3. **Image Upload**:
   - Upload images to the system, triggering automatic recognition with AWS Rekognition.

4. **Image Processing**:
   - Perform operations such as cropping, resizing, compression, rotation, thumbnail creation, and color adjustments.
   - Download processed images.

5. **Gallery Retrieval**:
   - Retrieve all tags associated with the user's images.
   - Search for and view all images under a specific tag.

6. **Image Download**:
   - Download original or processed images.

7. **Image Deletion**:
   - Remove specific images from their collection.

8. **Add User**:
   - Add new users to the system.

---

### Server-Side Features:
1. **Image Storage**:
   - Images are stored securely in AWS S3.

2. **Image Recognition**:
   - AWS Rekognition detects objects and labels in uploaded images, storing metadata such as labels, confidence scores, and S3 paths in an RDS database.

3. **Metadata Management**:
   - Metadata is dynamically managed for efficient storage and retrieval in RDS (MySQL).

4. **Image Processing**:
   - Images retrieved from S3 are processed using AWS Lambda and the Pillow library for resizing, color changing, and other transformations based on user configurations.

5. **Gallery Management**:
   - Dynamically query the database to retrieve image URLs based on user-selected labels.

---

## Architecture

### Core AWS Services:
1. **AWS S3**:
   - Stores all user-uploaded images and processed outputs.

2. **AWS Lambda**:
   - Handles image processing, recognition triggers, and metadata management.

3. **AWS Rekognition**:
   - Provides object and label recognition with confidence scoring.

4. **AWS RDS (MySQL)**:
   - Stores image metadata for efficient query and retrieval.

### Workflow:
1. Users upload an image.
2. The server triggers AWS Rekognition to analyze the image, extracting labels and storing metadata in the database.
3. Users can process images through the client interface, invoking Lambda functions for transformations.
4. Metadata queries enable users to retrieve images dynamically by tags or labels.

---

## API Endpoints

### User Operations:
- List all users: /users -GET
- Add new user:/addUser -POST

### Image Operations:
- List all images of a user: /images/{userId} -GET
- Upload a photo: /upload/{userId} -POST
- Delete a photo: /delete/{userId} -DELETE
- Process Image:

### Gallery Operations:
- Retreive lables:  /gallery/{userid}   
- Retreive gallery: /gallery/{userid}/{selected_lable}      



---

## Getting Started

### Prerequisites:
- AWS account with permissions for Lambda, S3, Rekognition, and RDS.
- MySQL database set up in AWS RDS.

### Installation:
1. Clone the repository.
2. Configure AWS credentials in the project.
3. Set up the MySQL database and update connection details in the configuration.
4. Deploy Lambda functions via AWS CLI or SAM.

### Usage:
1. Start the client-side application.
2. Upload images and explore processing, recognition, and gallery retrieval functionalities.

---

## License
This project is licensed under the [MIT License](LICENSE).

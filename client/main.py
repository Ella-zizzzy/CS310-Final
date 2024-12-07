#
# Client-side python app for Pixel-tailor app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to build 
# an intelligent image processing and management platform.
# Allow users to upload, process, and retrieve photo by lables we recognized
# 
#
# Authors:

# Shuyi Han
# Ziyue Li 
# Rongwei Peng
#
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   CS 310
#

import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import random

from configparser import ConfigParser


############################################################
#
# classes
#
'''
class User:

  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]


class Job:

  def __init__(self, row):
    self.jobid = row[0]
    self.userid = row[1]
    self.status = row[2]
    self.originaldatafile = row[3]
    self.datafilekey = row[4]
    self.resultsfilekey = row[5]
'''
class User:
  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.password = row[2]
    self.bucketfolder = row[3]

class Photo:
  def __init__(self, row):
    self.photoid = row[0]
    self.userid = row[1]
    self.original_name = row[2]
    self.bucketkey = row[3]

class Lable:
  def __init__(self, row):
    self.lableid = row[0]
    self.lablename = row[1]
    self.photoid = row[2]
    self.userid = row[3]

###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 480, 481, 482, 500]:
        #
        # we consider this a successful call and response
        #
        break

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
    

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => add new user")
    print("   2 => list all users")
    print("   3 => list all photos of a user")
    print("   4 => upload and recognition")
    print("   5 => delete photo")
    print("   6 => retrieve gallery by labels")
    

    #print("   3 => reset database")
    #print("   4 => upload pdf")
    #print("   5 => download results")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


############################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()

    #
    # let's map each row into a User object:
    #
    users = []
    for row in body:
      user = User(row)
      users.append(user)
    #
    # Now we can think OOP:
    #
    if len(users) == 0:
      print("no users...")
      return

    for user in users:
      print(" - User Id: ",user.userid)
      print("   User Name: ", user.username)
    #
    return

  except Exception as e:
    logging.error("**ERROR: users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# addusers
#
def addusers(baseurl):
  """
  Add a new user to the app

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:

    print("Enter the user name>")
    username = input()

    if username == "":
      print("Please enter the valid username.")
      return

    print("Enter the password>")
    password = input()

    if password == "":
      print("Please enter the valid username.")
      return

    bucketfolder = f"{uuid.uuid4()}"

    api = '/adduser'
    url = baseurl + api


    data = {"username": username, "password": password, "bucketfolder": bucketfolder}

    res = requests.post(url, json=data)
    
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    body = res.json()
    newid = body["userId"]
    print("The user ", newid, " is added successfully")
    return

  except Exception as e:
    logging.error("**ERROR: users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# List photos
#
def listphotos(baseurl):

    """
    List all the photos information of the user.

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """
    try:

      print("Enter user id>")
      userid = input()

      #get labels of the input userid TODO what is our api
      api = f"/listphotos/{userid}"
      url = baseurl + api
      res = web_service_get(url)

      if res is None:
        print("Fail to list photos.")
        return

      if res.status_code == 400:
        print(res.json())
        return

      if res.status_code !=200:
        print(f"Fail with status code: {res.status_code}")

      #successful 200
      photos = res.json()

      if not photos:
        print(f"No photos found for user {userid}")
        return


      ##display all the photos
      print(f"\nList all photos of user {userid}:")
      for photo in photos:
          print(f"  \nPhoto Details:")
          print(f"  User ID: {photo[1]}")
          print(f"  Photo ID: {photo[0]}")
          print(f"  Photo Original Name: {photo[2]}")
          print("\n")    


    except Exception as e:
      logging.error("**ERROR: listphotos() failed:")
      logging.error(e)
      print("An unexpected error occurred:", e)




############################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that photo to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    print("NOTE: Only .jpg, .jpeg, .png are allowed")
    print("Enter photo's filename>")
    local_filename = input()

    if not pathlib.Path(local_filename).is_file():
      print("File '", local_filename, "' does not exist...")
      return

    print("Enter user id>")
    userid = input()

    #
    # build the data packet. First step is read the PDF
    # as raw bytes:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the pdf as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    
    datastr = base64.b64encode(bytes).decode('utf-8')
    
    data = {"filename": local_filename, "data": datastr}

    #
    # call the web service:
    #
    api = f"/upload/{userid}"
    url = baseurl + api
    res = requests.post(url, json=data)
    
    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    elif res.status_code == 400: # no such user
      body = res.json()
      print(body)
      return
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, extract photoid:
    #
    body = res.json()
    newid = body["photoid"]
    print("The photo ",newid," was uploaded successfully")
    return

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# download
#
def download(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """
  
  try:
    print("Enter job id>")
    jobid = input()
    
    #
    # call the web service:
    #
    api = f"/results/{jobid}"
    url = baseurl + api
    res = web_service_get(url)
    
    # TODO ???

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    elif res.status_code == 400: # no such job
      body = res.json()
      print(body)
      return
    elif res.status_code in [480, 481, 482]:  # uploaded
      msg = res.json()
      print("No results available yet...")
      print("Job status:", msg)
      return
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return
      
    #
    # if we get here, status code was 200, so we
    # have results to deserialize and display:
    #
    
    body = res.json()
    
    # deserialize the message body:
    # TODO: body = ???

    datastr = body

    #
    # encode the data string to obtain the raw bytes in base64,
    # then call b64decode to obtain the original raw bytes.
    # Finally, decode() the bytes to obtain the results as a 
    # printable string.
    #
    
    results = ""
    base64_bytes = datastr.encode('utf-8')  
    bytes = base64.b64decode(base64_bytes) 
    results = bytes.decode('utf-8') 
    # TODO: base64_bytes = ???
    # TODO: bytes = ???
    # TODO: results = ???

    print(results)
    return

  except Exception as e:
    logging.error("**ERROR: download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
    

############################################################
#
# delete
#
def delete(baseurl):
  """
  Prompts the user for a local filename and user id.
  Delete that photo

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    
    print("Enter user id>")
    userid = input()

    print("Enter photo id>")
    photoid = input()

    api = f"/delete/{userid}"
    url = baseurl + api
    data = {"photoid":photoid}

    res = requests.delete(url, json=data)
    
    if res.status_code == 200: #success
      pass
    elif res.status_code == 400: 
      body = res.json()
      print(body)
      return
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        
        body = res.json()
        print("Error message:", body)

      return

    #
    # success, extract photoid:
    #
    print("The photo ",photoid," was deleted successfully.")
    return

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return



############################################################
#
# Retrieval photos by labels
#
def retrieve_user_labels_and_images(baseurl):

    """
    Retrieves and displays labels for a specific user,
    then allows drilling down into images for a specific label.

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """
    try:

      print("Enter user id")
      userid = input()

      #get labels of the input userid TODO what is our api
      api_labels = f"/label/{userid}"
      url_labels = baseurl + api_labels
      res_labels = web_service_get(url_labels)

      if res_labels is None:
        print("Fail to retrievev labels.")
        return

      if res_labels.status_code == 400:
        print(res_labels.json())
        return

      if res_labels.status_code !=200:
        print(f"Fail with status code: {res_labels.status_code}")

      #successful 200
      labels = res_labels.json()

      if not labels:
        print(f"No labels found for user {userid}")
        return

      ##display all the labels
      print(f"Lable for user {userid}:")
      for label in labels:
        print(f" - {label} \n")

      
      #prompt for user to select which label they want contain in the photo or EXIT

      while True:
        print("Enter a label to retrieve your photos (or 'E' to EXIT)>")
        selected_label = input()

        if selected_label == 'E' or selected_label == 'e':
          return

        api_photos = f"/labelphoto/{userid}/{selected_label}"
        url_photos = baseurl + api_photos
        res_photos = web_service_get(url_photos)

        if res_photos is None:
          print("Fail to retrieve photos.")
          continue

        if res_photos.status_code == 400:
          print(res_photos.json())
          continue

        if res_photos.status_code != 200:
          print(f"Failed with status code: {res_images.status_code}")
          continue

        #photos infomation
        photos = res_photos.json()

        if not photos:
          print(f"No photos found for label {selected_label}")
          continue

        ##display all the labels
        print(f"\nPhotos with label {selected_label}:")
        for photo in photos:
          print(f"  \nPhoto Details:")
          print(f"  User ID: {photo.get('userid', 'N/A')}")
          print(f"  Photo ID: {photo.get('photoid', 'N/A')}")
          print(f"  Lable Name: {photo.get('labelname', 'N/A')}")
          print(f"  Photo Original Name: {photo.get('original_name', 'N/A')}")
          print("\n")



    except Exception as e:
      logging.error("**ERROR: retrieve_user_labels_and_images() failed:")
      logging.error(e)
      print("An unexpected error occurred:", e)

############################################################
# main
#
try:
  print('** Welcome to PixelTailor **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'final-project-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      addusers(baseurl)
    elif cmd == 2:
      users(baseurl) 
    elif cmd == 3:
      listphotos(baseurl)
    elif cmd == 4:
      upload(baseurl)
    elif cmd == 5:
      delete(baseurl)
    elif cmd == 6:
      retrieve_user_labels_and_images(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)



#!/bin/bash
#
# Linux/Mac BASH script to build docker container
#
docker rmi 310-final-proj-client
docker build -t 310-final-proj-client .

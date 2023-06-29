#!/bin/bash

CONTAINER_NAME="my-redis-container"
DOCKER_IMAGE="redis"

# Check if the container exists
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    # Container exists, start it
    echo "Starting the existing container: $CONTAINER_NAME"
    docker start $CONTAINER_NAME
else
    # Container doesn't exist, create and run it
    echo "Creating and starting a new container: $CONTAINER_NAME"
    docker run -d --name $CONTAINER_NAME -p 6379:6379 $DOCKER_IMAGE
fi
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


MONGO_CONTAINER_NAME="my-mongo-db"
MONGO_PORT=27017
MONGO_DATABASE="transactions_db"
COLLECTION_NAME="transactions"

# Check if the container is already running
if [[ "$(docker ps -q -f name=$MONGO_CONTAINER_NAME)" ]]; then
    echo "MongoDB container is already running"
else
    # Run the MongoDB container
    docker run -d --name $MONGO_CONTAINER_NAME -p $MONGO_PORT:27017 -e MONGO_INITDB_DATABASE=$MONGO_DATABASE mongo
    echo "MongoDB container started"
fi


docker exec -it $MONGO_CONTAINER_NAME mongosh $MONGO_DATABASE --eval "db.$COLLECTION_NAME.createIndex({ cbu: 1 })" --quiet
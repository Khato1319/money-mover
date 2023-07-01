#!/bin/bash

# Define the Docker container and PostgreSQL connection details
POSTGRES_CONTAINER_NAME="moneymover-users-paymentmethods-postgres"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your_password"
POSTGRES_DB="your_database"
export PGPASSWORD="$POSTGRES_PASSWORD"

# Check if the container is already created
if docker ps -a -q -f "name=$POSTGRES_CONTAINER_NAME" --format '{{.Names}}' | grep -q "$POSTGRES_CONTAINER_NAME"; then
    echo "Starting existing PostgreSQL container..."
    docker start "$POSTGRES_CONTAINER_NAME"
else
  # Container does not exist, create and run it
  echo "Creating and running PostgreSQL container..."
  docker run -d --name "$POSTGRES_CONTAINER_NAME" \
    -e POSTGRES_USER="$POSTGRES_USER" \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -e POSTGRES_DB="$POSTGRES_DB" \
    -p 5433:5432 \
    postgres
fi

sleep 5

  # Define the SQL statements to create the tables
  SQL_CREATE_TABLE_1="CREATE TABLE IF NOT EXISTS Users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, pwd_hash VARCHAR(100) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, phone_number VARCHAR(12) NOT NULL UNIQUE, cuit VARCHAR(13) NOT NULL UNIQUE);"
  SQL_CREATE_TABLE_2="CREATE TABLE IF NOT EXISTS PaymentMethods (money_key VARCHAR(255) PRIMARY KEY, bank_name TEXT NOT NULL, bank_cbu VARCHAR(22) NOT NULL UNIQUE, user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES Users(id));"

  # Execute the SQL statements inside the container
  docker exec -it "$POSTGRES_CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -c "$SQL_CREATE_TABLE_1" \
    -c "$SQL_CREATE_TABLE_2"


MONGO_CONTAINER_NAME="moneymover-transactions-mongo"
MONGO_PORT=27017
MONGO_DATABASE="transactions_db"
COLLECTION_NAME="transactions"

# Check if the container is already running
if [[ "$(docker ps -a -q -f name=$MONGO_CONTAINER_NAME)" ]]; then
    echo "MongoDB container is already running"
    docker start $MONGO_CONTAINER_NAME
else
    # Run the MongoDB container
    docker run -d --name $MONGO_CONTAINER_NAME -p $MONGO_PORT:27017 -e MONGO_INITDB_DATABASE=$MONGO_DATABASE mongo
    echo "MongoDB container started"
fi

sleep 5

docker exec -it $MONGO_CONTAINER_NAME mongosh $MONGO_DATABASE --eval "db.$COLLECTION_NAME.createIndex({ user_id: 1 })" --quiet
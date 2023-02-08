#!/bin/bash

docker stop seamless-database-container
docker rm seamless-database-container
set -u -e
rm -rf seamless-db
mkdir seamless-db
seamless-database seamless-db
sleep 10
docker logs seamless-database-container
sleep 10
docker stop seamless-database-container
docker rm seamless-database-container
rm -f data-checksums.list
for f in $(find data/ -type f); do
    checksum=$(seamless-checksum $f) # wrapper around "openssl dgst -sha3-256"
    echo $f $checksum >> data-checksums.list
    echo $f $checksum
    ln $f seamless-db/buffers/$checksum -f
done
#!/bin/bash

set -u -e
checksum_file=$1
outfile=$2
rm -rf TEMP
mkdir TEMP
cp -rl seamless-db TEMP/seamless-db
for i in `cat ${checksum_file}`; do
  rm -f TEMP/seamless-db/buffers/$i
done
cd TEMP
tar czf TEMP.tgz seamless-db/
cd ..
mv -f TEMP/TEMP.tgz $outfile
rm -rf TEMP

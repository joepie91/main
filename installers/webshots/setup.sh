#!/bin/bash
cd ~
git clone git://github.com/ArchiveTeam/webshots-grab.git
if [ $? -ne 0 ]; then echo "[X] Retrieving the grabber code failed. Exiting..."; exit 1; fi

cd webshots-grab
./get-wget-lua.sh
if [ $? -ne 0 ]; then echo "[X] Compiling wget-lua failed. Exiting..."; exit 1; fi

echo "What username would you like to use? "
read USERNAME
echo "How many threads? (start out with 2 or so) "
read THREADCOUNT
echo "run-pipeline --concurrent $THREADCOUNT ~/webshots-grab/pipeline.py $USERNAME" > ./start.sh
chmod +x ./start.sh
echo "Done! Run ~/webshots-grab/start.sh as the 'archiveteam' user to start grabbing."

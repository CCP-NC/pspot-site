#!/usr/bin/bash

# A script to push the website and its content up to a given URL
FILE_LIST="graphs data pspot_data.json"

echo "What to push?"
select pmode in "All" "Just library data"; do
	case $pmode in
		"All" ) # Add all the other files
			FILE_LIST=$FILE_LIST" index.html pspot.html stylesheet.css favicon.ico js lib"
			break;;	
		"Just library data" ) break;;
	esac
done

URL=""
CONFIRM="n"

while 
	[ $CONFIRM != "y" ]
do
	read -p "Enter the destination URL: " URL
	echo "You are about to copy the following files: "
	echo $FILE_LIST
	echo "to the following URL: "
	echo $URL
	read -p "Confirm [y/n]?" CONFIRM
done

scp -r $FILE_LIST $URL
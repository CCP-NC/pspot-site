#!/bin/bash

# A script to push the website and its content up to a given URL
DATA_LIST="graphs data pspot_data.json"
SITE_LIST="index.html pspot.html help stylesheet.css favicon.ico js lib"
HELP_LAYOUT="github"
DEFAULT_URL="ccpnc@webs.materials.ox.ac.uk:public_html/pspot_site"

echo "What to push?"
select pmode in "All" "Just library data" "Just website"; do
	case $pmode in
		"All" ) # Add all the other files
			# First, compile help
			generate-md --layout $HELP_LAYOUT --input help.md --output help
			FILE_LIST=$DATA_LIST" "$SITE_LIST
			break;;	
		"Just library data" ) 
			FILE_LIST=$DATA_LIST
			break;;
		"Just website" )
			generate-md --layout $HELP_LAYOUT --input help.md --output help
			FILE_LIST=$SITE_LIST
			break;;			
	esac
done

URL=""
CONFIRM="n"

while 
	[ $CONFIRM != "y" ]
do
	echo "Push to default URL "$DEFAULT_URL" ?"
	select umode in "Yes" "No"; do
		case $umode in
			"Yes" )
				URL=$DEFAULT_URL
				break;;
			"No" )
				read -p "Enter the destination URL: " URL
				break;;
		esac
	done
	echo "You are about to copy the following files: "
	echo $FILE_LIST
	echo "to the following URL: "
	echo $URL
	read -p "Confirm [y/n]?" CONFIRM
done

scp -r $FILE_LIST $URL

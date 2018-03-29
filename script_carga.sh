#!/bin/sh

if [ $# -eq 0 ]; then
	echo "${0}: No path specified"
	exit
fi

if [ ! -d "$1" ]; then
	echo "${0}: cannot access ${1}: directory or file doesn't exist"
	exit
fi

INPUT_PATH=$1
OUTPUT_PATH="${INPUT_PATH}processed/"
FAILED_PATH="${INPUT_PATH}errors/"
LOGS_PATH="${INPUT_PATH}logs/"

if [ ! -d "$OUTPUT_PATH" ]; then
	mkdir "$OUTPUT_PATH"
fi

if [ ! -d "$FAILED_PATH" ]; then
        mkdir "$FAILED_PATH"
fi

if [ ! -d "$LOGS_PATH" ]; then
        mkdir "$LOGS_PATH"
fi


OUTPUT=""

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

for file in "${INPUT_PATH}"*.json
do
	echo "Processing " $(basename "$file")...
	OUTPUT=$( { python ./manage.py load_products "${file}" --cat_base "Brands > Volvo Penta"; } 2>&1 )
	LOG_FILE=$(basename "$file").log
	LOG_FILE="${LOGS_PATH}${LOG_FILE}"
	touch "$LOG_FILE"
	echo "Log file saved in $LOG_FILE"
	echo "$OUTPUT" > "$LOG_FILE"
	echo "$OUTPUT" | grep -i "Error"
	RETVAL=$?
	if [ ! $RETVAL -eq 0 ]; then
		mv "$file" "$OUTPUT_PATH"
		printf "${GREEN}COMPLETED SUCCESSFULLY. ${file} loaded and moved to ${OUTPUT_PATH}${NC}\n"
	else
		mv "$file" "$FAILED_PATH"
                printf "${RED}FAILED. ${file} moved to ${FAILED_PATH}${NC}\n"
	fi
	OUTPUT=""
done

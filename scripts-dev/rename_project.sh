#!/bin/bash -e

# Check that regex-rename is installed
if ! command -v regex-rename &> /dev/null
then
    echo "regex-rename python module not found. Please run 'python -m pip install regex-rename'"
    exit 1
fi

# Allow specifying either:
# * One argument, which is the new project name, assuming the old project name is "my project name"
# * Or two arguments, where one can specify 1. the old project name and 2. the new project name
if [ $# -eq 1 ]; then
    PLACEHOLDER="my project name"
    REPLACEMENT=$1
elif [ $# -eq 2 ]; then
    PLACEHOLDER=$1
    REPLACEMENT=$2
else
    echo "Usage:"
    echo "./"$(basename "$0") "\"new name\""
    echo "./"$(basename "$0") "\"old name\" \"new name\""
    exit 1
fi

PLACEHOLDER_DASHES=$(echo $PLACEHOLDER | sed 's/ /-/g')
PLACEHOLDER_UNDERSCORES=$(echo $PLACEHOLDER | sed 's/ /_/g')

REPLACEMENT_DASHES=$(echo $REPLACEMENT | sed 's/ /-/g')
REPLACEMENT_UNDERSCORES=$(echo $REPLACEMENT | sed 's/ /_/g')

echo "Updating file and folder names..."

regex-rename --rename "(.*)$PLACEHOLDER_DASHES(.*)" "\1$REPLACEMENT_DASHES\2" > /dev/null
regex-rename --rename "(.*)$PLACEHOLDER_UNDERSCORES(.*)" "\1$REPLACEMENT_UNDERSCORES\2" > /dev/null

echo "Updating references within files..."

# Iterate through each file and replace strings within files
for file in $(grep --exclude-dir=env --exclude-dir=venv -lEw "$PLACEHOLDER_DASHES|$PLACEHOLDER_UNDERSCORES" -R *); do
    if [[ $file != $(basename "$0") ]]; then
        sed -i "s/$PLACEHOLDER_DASHES/$REPLACEMENT_DASHES/g" $file
        sed -i "s/$PLACEHOLDER_UNDERSCORES/$REPLACEMENT_UNDERSCORES/g" $file
        echo " - $file"
    fi
done

echo "Done!"

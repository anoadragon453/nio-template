#!/bin/bash -e

# Check that regex-rename is installed
if ! command -v regex-rename &> /dev/null
then
    echo "regex-rename python module not found. Please run 'python -m pip install regex-rename'"
    exit 1
fi

# GNU sed and BSD(Mac) sed handle -i differently :(
function is_gnu_sed(){
    sed --version >/dev/null 2>&1
}

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

PLACEHOLDER_DASHES="${PLACEHOLDER// /-}"
PLACEHOLDER_UNDERSCORES="${PLACEHOLDER// /_}"

REPLACEMENT_DASHES="${REPLACEMENT// /-}"
REPLACEMENT_UNDERSCORES="${REPLACEMENT// /_}"

echo "Updating file and folder names..."

# Iterate over all directories (besides venv's and .git) and rename files/folders
# Yes this looks like some crazy voodoo, but it's necessary as regex-rename does
# not provide any sort of recursive functionality...
find . -type d -not -path "./env*" -not -path "./.git" -not -path "./.git*" \
  -exec sh -c "cd {} && \
    regex-rename --rename \"(.*)$PLACEHOLDER_DASHES(.*)\" \"\1$REPLACEMENT_DASHES\2\" && \
    regex-rename --rename \"(.*)$PLACEHOLDER_UNDERSCORES(.*)\" \"\1$REPLACEMENT_UNDERSCORES\2\"" \; > /dev/null

echo "Updating references within files..."

# Iterate through each file and replace strings within files
for file in $(grep --exclude-dir=env --exclude-dir=venv --exclude-dir=.git --exclude *.pyc -lEw "$PLACEHOLDER_DASHES|$PLACEHOLDER_UNDERSCORES" -R * .[^.]*); do
    echo "Checking $file"
    if [[ $file != $(basename "$0") ]]; then
        if is_gnu_sed; then
            sed -i "s/$PLACEHOLDER_DASHES/$REPLACEMENT_DASHES/g" $file
            sed -i "s/$PLACEHOLDER_UNDERSCORES/$REPLACEMENT_UNDERSCORES/g" $file
        else
            sed -i "" "s/$PLACEHOLDER_DASHES/$REPLACEMENT_DASHES/g" $file
            sed -i "" "s/$PLACEHOLDER_UNDERSCORES/$REPLACEMENT_UNDERSCORES/g" $file
        fi
        echo " - $file"
    fi
done

echo "Done!"

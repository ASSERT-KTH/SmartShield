#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <solidity_file> <main_contract> <outputfile>"
    exit 1
fi

# CSV filename
path="$1"
main_contract=$2
outputfile=$3

echo "Compiling the Solidity file '$path'..."

# Check if the CSV file exists
if [ ! -f "$path" ]; then
    echo "Error: file '$path' not found."
    exit 1
fi

if [[ "$path" == *.sol ]]; then
    # Extract pragma versions from the file
    echo "Extracting pragma version from the file..."
    pragma_version=$(grep -oP '^\s*pragma\s+solidity\s+[\^><=]*\K\d+\.\d+\.\d+' "$path" | sed 's/[\^><=]//g')
    # echo $pragma_version
    if [ -n "$pragma_version" ]; then
        solc-select use --always-install "$pragma_version"
        output=$(solc --bin-runtime "$path")

        bin=$(echo "$output" | grep -A 2 "$main_contract =======" | tail -n 1)
        printf "%s" "$bin" > "$outputfile"
    fi
fi

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
    output=$(solc --bin-runtime "$path" --optimize --optimize-runs 200)

    bin=$(echo "$output" | grep -A 2 "$main_contract =======" | tail -n 1)
    printf "%s" "$bin" > "$outputfile"
    # fi
fi

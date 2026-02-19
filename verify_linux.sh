#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}========================================================${NC}"
echo -e "${CYAN}           SIMPLE ISO VERIFIER (Linux/Mac)              ${NC}"
echo -e "${CYAN}========================================================${NC}"
echo
echo "1. Drag and Drop your ISO/File into this terminal and hit ENTER."
echo

read -p "File Path: " filepath
# Remove single quotes if drag/drop adds them
filepath="${filepath//\'/}"
# Remove backslash escapes if present (drag/drop behavior on some terminals)
filepath=$(eval echo "$filepath")

if [ ! -f "$filepath" ]; then
    echo -e "${RED}[ERROR] File not found!${NC}"
    exit 1
fi

echo
echo "Calculating SHA256 hash... Please wait..."
echo

# Detect tool
if command -v sha256sum &> /dev/null; then
    # Linux
    hash_output=$(sha256sum "$filepath" | awk '{print $1}')
elif command -v shasum &> /dev/null; then
    # Mac
    hash_output=$(shasum -a 256 "$filepath" | awk '{print $1}')
else
    echo -e "${RED}Error: Neither sha256sum nor shasum found.${NC}"
    exit 1
fi

echo "Calculated Hash: $hash_output"
echo
echo "2. Paste the expected SHA256 hash below:"
echo

read -p "Expected Hash: " expected
# Trim whitespace
expected=$(echo "$expected" | xargs)

# Case insensitive comparison
if [[ "${hash_output,,}" == "${expected,,}" ]]; then
    echo
    echo -e "${GREEN}========================================================${NC}"
    echo -e "${GREEN}                  SUCCESS: MATCH VERIFIED               ${NC}"
    echo -e "${GREEN}========================================================${NC}"
    echo
    echo "The file is authentic."
else
    echo
    echo -e "${RED}========================================================${NC}"
    echo -e "${RED}                  WARNING: HASH MISMATCH                ${NC}"
    echo -e "${RED}========================================================${NC}"
    echo
    echo "Calculated: $hash_output"
    echo "Expected:   $expected"
    echo
    echo "The file may be corrupted or modified!"
fi

echo
read -p "Press Enter to exit..."

#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <variant_name>"
    echo "Example: $0 mean_shift_matrix"
    exit 1
fi

VARIANT="$1"

echo "Compiling variant: $VARIANT"

executable="./build/${VARIANT}"
if [[ -f "$executable" ]]; then
    # echo "Warning: $executable already exists and may be overwritten by recompilation."
    # read -p "Recompile $VARIANT? (y/n): " answer
    # [[ "$answer" != "y" ]] && exit 0
    echo "$VARIANT already compiled. Skipping compilation."
    exit 0
fi

# Clean previous build and compile
make -C build clean
make -C build "$VARIANT"

if [[ $? -eq 0 ]]; then
    echo "Compilation of $VARIANT successful."
else
    echo "Compilation of $VARIANT failed."
    exit 2
fi
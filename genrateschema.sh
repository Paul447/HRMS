#!/bin/bash

# Folder where schemas will be saved
OUTPUT_DIR="schemas"

# Create the folder if it doesn't exist
mkdir -p $OUTPUT_DIR

apps=(
    "hrmsauth"
    "usermanagement"
    "department"
    "payfrequency"
    "employeetype"
    "yearofexperience"
    "accuralrates"
    "ptobalance"
    "timeclock"
    "shiftmanagement"
    "leavetype"
    "payperiod"
    "holiday"
    "punchreport"
    "onshift"
    "timeoff_management"
    "adminorganizer"
    "deptleaves"
    "allowipaddress"
    "notificationapp"
    "sickpolicy"
    "unverifiedsickleave"
    "timeoffreq"
    "usertimeoffbalance"
    "decisionedtimeoff"
)

for app in "${apps[@]}"; do
    echo "Generating schema for $app..."
    
    DOT_FILE="${OUTPUT_DIR}/${app}.dot"
    PNG_FILE="${OUTPUT_DIR}/${app}.png"
    
    # Generate .dot file
    python manage.py graph_models $app --output "$DOT_FILE" --pydot --verbose-names
    
    # Convert .dot to high-quality PNG
    dot -Tpng "$DOT_FILE" -o "$PNG_FILE" -Gdpi=300
done

echo "All schemas generated in folder: $OUTPUT_DIR"

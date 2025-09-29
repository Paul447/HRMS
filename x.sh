#!/bin/bash

# Folder where schemas will be saved
OUTPUT_DIR="schemas"

# Create the folder if it doesn't exist
mkdir -p $OUTPUT_DIR

# List of apps
apps=(
    "hrmsauth"
    "usermanagement"
    "department"
    "payfrequency"
    "employeetype"
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

# Join apps into a single space-separated string
ALL_APPS="${apps[*]}"

# Output files
DOT_FILE="${OUTPUT_DIR}/all_apps.dot"
PNG_FILE="${OUTPUT_DIR}/all_apps.png"

echo "Generating combined schema for all apps..."

# Generate .dot file for all apps
python manage.py graph_models $ALL_APPS --output "$DOT_FILE" --pydot --verbose-names --group-models

# Convert .dot to high-quality PNG
dot -Tpng "$DOT_FILE" -o "$PNG_FILE" -Gdpi=300

echo "Combined schema generated: $PNG_FILE"

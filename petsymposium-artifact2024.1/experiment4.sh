#!/bin/sh

static_mapping_folder=output_web/static
override_folder=output_web/override
# Move to root of git repository
cd ..
mkdir -p $static_mapping_folder

# Classify Static Mapping (override)
./classify_override.sh

#Compare classifications
python3 classify_analysis.py compare_override_to_static $override_folder $static_mapping_folder

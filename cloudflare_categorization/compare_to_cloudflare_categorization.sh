#!/bin/bash

output_folder=output_web/cloudflare
cloudflare_output=$output_folder/cloudflare.csv
topics_output=output_web/crux/chrome.csv

mapping=cloudflare_categorization/cloudflare_categories_manual_mapping_topics.json
mapping_dict=$output_folder/mapping_categories.pickle

crux_dependencies_path=sandbox_dependencies/topics_web/crux.csv

cd ..
python3 classify_analysis.py compare_to_cloudflare $topics_output $cloudflare_output $mapping $output_folder $mapping_dict $crux_dependencies_path

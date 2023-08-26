#!/bin/bash

if [ $# -eq 0 ]
then
    echo "No argument supplied, you need to specify the number of domains to verify"
else
    cd ..
    nb_domains=$1
    crux_path=output_web/crux/chrome.csv
    output_folder=output_web/manual_verification

    mkdir -p $output_folder

    python3 classify_analysis.py manual_verification $nb_domains $crux_path $output_folder

fi
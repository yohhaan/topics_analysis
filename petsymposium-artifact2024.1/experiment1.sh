#!/bin/sh

# To completely reproduce the analysis of the paper
complete_evaluation=false

static_mapping_folder=output_web/static
# Move to root of git repository
cd ..
mkdir -p $static_mapping_folder

# Plot graphs and stats about Static Mapping released by Google
python3 classify_analysis.py extract_stats_static $static_mapping_folder

# Classify CrUX and plot graphs and stats
./classify_crux.sh

if [ "$complete_evaluation" = true ]
then
    #Classify Tranco and Wordnet as well and plot graphs and stats
    ./classify_tranco.sh
    ./classify_web_wordnet.sh
fi

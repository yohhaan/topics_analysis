#!/bin/sh

# To completely reproduce the analysis of the paper
complete_evaluation=false

# Move to root of git repository
cd ..

# Classify Static Mapping (override) and CrUX and plot graphs and stats
./classify_override.sh
./classify_crux.sh

if [ "$complete_evaluation" = true ]
then
    #Classify Tranco and Wordnet as well and plot graphs and stats
    ./classify_tranco.sh
    ./classify_web_wordnet.sh
fi

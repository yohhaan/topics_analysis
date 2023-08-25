#!/bin/sh

# If we want to go for the complete reproduction of the analysis
longer_evaluation=false

# Move to root of git repository
cd ..

# Classify Static Mapping (override) and CrUX
./classify_override.sh
./classify_crux.sh
# Plot graphs in figs/ folder and extract stats
python3 classify_analysis.py override
python3 classify_analysis.py crux

if [ "$longer_evaluation" = true ]
then
    #Classify Tranco and Wordnet as well
    ./classify_tranco.sh
    ./classify_web_wordnet.sh
    # Plot graphs in figs/ folder and extract stats
    python3 classify_analysis tranco
    python3 classify_analysis wordnet
fi


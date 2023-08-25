#!/bin/sh

# If we want to go for the complete reproduction of the analysis
longer_eval=false
longer_evaluation

# Move to root of git repository


if [ "$longer_evaluation" = true ]
then
    top=10000
else
    top=100
    #Quick eval and we do not have the Wordnet classification to extract the word classified with highest confidence for each topic, so here it is.
    mkdir -p ../output/subdomains
    cp taxonomy.words ../output/subdomains/taxonomy.words
fi

cd ..
./subdomains_crafting.sh $top


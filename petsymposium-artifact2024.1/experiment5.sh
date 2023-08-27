#!/bin/sh

# To completely reproduce the analysis of the paper
complete_evaluation=false

if [ "$complete_evaluation" = true ]
then
    top=10000
else
    top=100
fi

# Move to root of git repository
cd ..
#Note: need to delete and recreate the folder between runs of experiment5 to
#take into account the possibility to switch from quick to long evaluation
rm -r output_web/crafted_subdomains
mkdir -p output_web/crafted_subdomains

# Check if WordNet was classified during experiment 1, if so, extract word
# classified with highest confideence for each topic. If not we use the provided
# file for quick evaluation
wordnet_path=output_web/wordnet/chrome_ml_model.csv
word_output_path=output_web/crafted_subdomains/taxonomy.words

if [ ! -f $wordnet_path ]
then
    cp petsymposium-artifact2024.1/taxonomy.words $word_output_path
else
    python3 subdomains.py extract $wordnet_path $word_output_path
fi

./subdomains_crafting.sh $top

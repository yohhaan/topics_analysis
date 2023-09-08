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

output_folder=output_web/crafted_subdomains_${top}

# Check if WordNet was classified during experiment 1, if so, extract word
# classified with highest confideence for each topic. If not we use the provided
# file for quick evaluation
wordnet_path=output_web/wordnet/chrome_ml_model.csv
word_output_path=$output_folder/taxonomy.words

mkdir -p $output_folder

if [ ! -f $word_output_path ]
then
    if [ ! -f $wordnet_path ]
    then
        cp petsymposium-artifact2024.1/taxonomy.words $word_output_path
    else
        python3 subdomains.py extract $wordnet_path $word_output_path
    fi
fi

./subdomains_crafting.sh $top

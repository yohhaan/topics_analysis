#!/bin/sh
output_folder=output/wordnet
domains=$output_folder/wordnet.domains
output=$output_folder/wordnet.csv
wordnet_path=./sandbox_dependencies/utils/wordnet/wordnet.words

mkdir -p $output_folder

if [ ! -f $domains ]
then
    cp $wordnet_path $domains
fi

if [ ! -f $output ]
then
    #Header
    python3 classify.py chrome_ml_model_csv_header >> $output
    #Parallel inference - we don't mind retaining the alphabetical order so no
    #-k
    parallel -X --bar -N 1000 -a $domains -I @@ "python3 classify.py chrome_ml_model_csv @@ >> $output"
fi
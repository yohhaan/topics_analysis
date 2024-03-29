#!/bin/sh
output_folder=output_web/validation
domains=$output_folder/validation.domains
output=$output_folder/chrome.csv
wordnet_path=./sandbox_dependencies/utils/wordnet/wordnet.words

cd ..
mkdir -p $output_folder

if [ ! -f $domains ]
then
    shuf -n 1000 $wordnet_path > $domains
fi


if [ ! -f $output ]
then
    #Header
    python3 classify.py chrome_csv_header >> $output
    #Parallel inference - we don't mind retaining the alphabetical order so no
    #-k
    parallel -X --bar -N 100 -a $domains -I @@ "python3 classify.py chrome_csv @@ >> $output"
fi
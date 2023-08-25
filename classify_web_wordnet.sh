#!/bin/sh
output_folder=output_web/wordnet
domains=$output_folder/wordnet.domains
output=$output_folder/chrome_ml_model.csv
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
    #Parallel inference
    parallel -X --bar -N 1000 -a $domains -I @@ "python3 classify.py chrome_ml_model_csv @@ >> $output"
fi

if [ -f $output ]
then
    #Plot graphs and extract stats
    python3 classify_analysis.py plots_and_stats $output_folder
fi
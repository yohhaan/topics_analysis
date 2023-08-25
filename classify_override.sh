#!/bin/sh
override_path=./sandbox_dependencies/topics_web/override_list.csv
output_folder=output/override
domains=$output_folder/override.domains
output=$output_folder/override.csv

mkdir -p $output_folder

if [ ! -f $domains ]
then
    cp $override_path $domains
fi

if [ ! -f $output ]
then
    #Header
    python3 classify.py chrome_ml_model_csv_header >> $output
    #Parallel inference - we don't mind retaining the alphabetical order so no
    #-k
    parallel -X --bar -N 100 -a $domains -I @@ "python3 classify.py chrome_ml_model_csv @@ >> $output"
fi
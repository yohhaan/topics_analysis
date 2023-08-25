#!/bin/sh
tranco_top_1m=./sandbox_dependencies/topics_web/top-1m.csv
output_folder=output_web/tranco
domains=$output_folder/tranco.domains
output=$output_folder/chrome.csv

mkdir -p $output_folder

if [ ! -f $domains ]
then
    sed -nr "s/[0-9]+,(.*)/\1/p" $tranco_top_1m > $domains
    sed -i 's/\r$//g' $domains
fi

if [ ! -f $output ]
then
    #Header
    python3 classify.py chrome_csv_header >> $output
    #Parallel inference
    parallel -X --bar -N 1000 -a $domains -I @@ "python3 classify.py chrome_csv @@ >> $output"
fi

if [ -f $output ]
then
    #Plot graphs and extract stats
    python3 classify_analysis.py plots_and_stats $output_folder
fi
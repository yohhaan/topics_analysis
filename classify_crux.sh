#!/bin/sh
crux_path=./sandbox_dependencies/topics_web/crux.csv
output_folder=output_web/crux
domains_temp=$output_folder/crux.domains_temp
domains=$output_folder/crux.domains
output=$output_folder/chrome.csv

mkdir -p $output_folder

if [ ! -f $domains ]
then
    sed -nr "s/https?:\/\/(.*),.*/\1/p" $crux_path > $domains_temp
    sort $domains_temp | uniq > $domains
    rm $domains_temp
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
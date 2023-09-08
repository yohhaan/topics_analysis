#!/bin/sh
taxonomy=./sandbox_dependencies/topics_web/taxonomy.md
crux=./sandbox_dependencies/topics_web/crux.csv

crux_classified_path=output_web/crux/chrome.csv


if [ $# -eq 0 ]
then
    echo "No argument supplied, you need to specify the number of domains for which subdomains must be created"
else
    top=$1

    output_folder=output_web/crafted_subdomains_${top}
    mkdir -p $output_folder

    words=$output_folder/taxonomy.words
    words_domains=$output_folder/words_subdomains.domains
    words_truth=$output_folder/words_subdomains_targeted.csv
    words_output=$output_folder/words_subdomains.csv
    results_path=$output_folder/words_results.csv

    if [ ! -f $words ]
    then
        echo "Words classified with highest confidence for each topic need to be extracted before pursuing"
    elif [ ! -f $words_domains ]
    then
        python3 subdomains.py create $crux $top $words $words_domains $words_truth
    fi

    if [ ! -f $words_output ]
    then
        #Header
        python3 classify.py chrome_csv_header >> $words_output
        # Parallel inference
        parallel -X --bar -N 1000 -a $words_domains -I @@ "python3 classify.py chrome_csv @@ >> $words_output"
    fi

    #extract results
    python3 subdomains.py results $crux_classified_path $words_output $words_truth $results_path $output_folder $crux $top
fi


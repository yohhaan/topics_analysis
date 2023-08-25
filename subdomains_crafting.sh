#!/bin/sh
taxonomy=./sandbox_dependencies/topics_web/taxonomy.md
crux=./sandbox_dependencies/topics_web/crux.csv
output_folder=output/subdomains

words=$output_folder/taxonomy.words
words_domains=$output_folder/words_subdomains.domains
words_truth=$output_folder/words_subdomains_targeted.csv
words_output=$output_folder/words_subdomains.csv

mkdir -p $output_folder

if [ $# -eq 0 ]
then
    echo "No argument supplied, you need to specify the number of domains for which subdomains must be created"
else
    top=$1
    if [ ! -f $words ]
    then
        python3 subdomains.py extract $words
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

    python3 subdomains.py results
fi




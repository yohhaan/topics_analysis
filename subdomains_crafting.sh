#!/bin/sh
taxonomy=./sandbox_dependencies/topics_web/taxonomy.md
crux=./sandbox_dependencies/topics_web/crux.csv
top=10000
output_folder=output/subdomains

topics=$output_folder/taxonomy.topics
topics_domains=$output_folder/topics_subdomains.domains
topics_truth=$output_folder/topics_targeted_subdomains.csv
topics_output=$output_folder/topics_subdomains.csv

words=$output_folder/taxonomy.words
words_domains=$output_folder/words_subdomains.domains
words_truth=$output_folder/words_targeted_subdomains.csv
words_output=$output_folder/words_subdomains.csv

mkdir -p $output_folder

if [ ! -f $topics ]
then
    ##to extract just last subtopic in the topics hierarchy:
    echo "Unknown" > $topics
    sed -nr "s/.*\/(.*)\s*\|/\1/p" $taxonomy >> $topics
    sed -i "s/[ \t]*$//g" $topics # remove trailing spaces
    sed -i "s/[^[:alpha:]]/-/g" $topics #replace any non alpha character by '-'
    sed -i "s/-\+/-/g" $topics #replace different occurences in row of '-' with only one '-'
fi

if [ ! -f $topics_domains ]
then
    python3 subdomains.py $crux $top $topics $topics_domains $topics_truth
fi

if [ ! -f $topics_output ]
then
    #Header
    python3 process.py chrome_csv_header >> $topics_output
    # Parallel inference
    parallel -X --bar -N 1000 -a $topics_domains -I @@ "python3 process.py chrome_csv @@ >> $topics_output"
fi

if [ ! -f $words ]
then
    echo "Extract top words for each topic"
elif [ ! -f $words_domains ]
then
    python3 subdomains.py $crux $top $words $words_domains $words_truth
fi

if [ ! -f $words_output ]
then
    #Header
    python3 process.py chrome_csv_header >> $words_output
    # Parallel inference
    parallel -X --bar -N 1000 -a $words_domains -I @@ "python3 process.py chrome_csv @@ >> $words_output"
fi


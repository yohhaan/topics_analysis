#!/bin/sh

crux_order_traffic=../output_web/simulator/crux_order_traffic.csv
crux_classified_path=../output_web/crux/chrome.csv

if [ $# -eq 0 ]
then
    echo "No argument supplied, you need to specify the number of users to generate"
else
    nb_users=$1
    output_folder=../output_web/simulator/${nb_users}_users
    input=$output_folder/${nb_users}_users.input
    output_topics=$output_folder/${nb_users}_users_topics.csv
    mkdir -p $output_folder

    if [ ! -f $input ]
    then
        python3 generate_users.py generate_parallel_input $nb_users $input
    fi

    # #To extract Domains Stats
    # output_domains=$output_folder/${nb_users}_users_domains.csv
    # if [ ! -f $output_domains ]
    # then
    #     echo "domain" >> $output_domains
    #     parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 generate_users.py domains $crux_order_traffic $crux_classified_path @@ >> $output_domains"
    # fi

    if [ ! -f $output_topics ]
    then
        echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output_topics
        parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 generate_users.py topics $crux_order_traffic $crux_classified_path @@ >> $output_topics"
    fi
fi
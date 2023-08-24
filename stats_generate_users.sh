#!/bin/sh
output_folder=output/simulator/synthetic_stats
input=$output_folder/52k_users.input
output_domains=$output_folder/52k_users_domains1.csv
output_topics=$output_folder/52k_users_topics.csv
mkdir -p $output_folder

if [ ! -f $output_domains ]
then
    echo "domain" >> $output_domains
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 stats_generate_users.py @@ >> $output_domains"
fi

if [ ! -f $output_topics ]
then
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output_topics
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output_topics"
fi
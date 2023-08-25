#!/bin/sh
output_folder=output/simulator/synthetic
input=$output_folder/52k_users.input
output=$output_folder/52k_users.csv

mkdir -p $output_folder

if [ ! -f $output ]
then
    #Header
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output"
fi



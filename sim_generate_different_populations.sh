#!/bin/sh
output_folder=output/simulator/synthetic

mkdir -p $output_folder

input=$output_folder/1k_users.input
output=$output_folder/1k_users.csv


if [ ! -f $output ]
then
    #Header
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output"
fi

input=$output_folder/5k_users.input
output=$output_folder/5k_users.csv


if [ ! -f $output ]
then
    #Header
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output"
fi


input=$output_folder/10k_users.input
output=$output_folder/10k_users.csv


if [ ! -f $output ]
then
    #Header
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output"
fi


input=$output_folder/50k_users.input
output=$output_folder/50k_users.csv


if [ ! -f $output ]
then
    #Header
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output"
fi

input=$output_folder/100k_users.input
output=$output_folder/100k_users.csv


if [ ! -f $output ]
then
    #Header
    echo "nb_unique_domain\tnb_topics\tt1\tt2\tt3\tt4\tt5" >> $output
    parallel -X --bar -N 1 --colsep ' ' -a $input -I @@ "python3 sim_generate_users.py @@ >> $output"
fi

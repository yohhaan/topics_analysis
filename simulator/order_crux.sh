#!/bin/sh

output_folder=../output_web/simulator
cloudflare_path=$output_folder/cloudflare-radar-domains-top100.csv
crux_path=../sandbox_dependencies/topics_web/crux.csv
tranco_path=../sandbox_dependencies/topics_web/top-1m.csv

output_offset_folder=$output_folder/crux_order
crux_order_path=$output_folder/crux_order.csv
crux_order_traffic_path=$output_folder/crux_order_traffic.csv

nb_domains=1000000
nb_proc_minus_one=15 #nb_cpus -1

if [ ! -d $output_offset_folder ]
then
    mkdir -p $output_offset_folder
    #reorder each range specified by offset
    seq 0 $nb_proc_minus_one | parallel --bar python3 order_crux.py order $cloudflare_path $crux_path $tranco_path $output_offset_folder $nb_domains $nb_proc_minus_one :::
fi

if [ ! -f $crux_order_traffic_path ]
then
    #merge
    python3 order_crux.py merge $output_offset_folder $crux_order_path $crux_order_traffic_path
fi

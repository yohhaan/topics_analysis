#!/bin/sh

output_simulator_folder=../output_web/simulator
output_folder=$output_simulator_folder/classifier
crux_order_traffic_path=.$output_simulator_folder/crux_order_traffic.csv
crux_classified_path=../output_web/crux/chrome.csv

nb_users=52000
users_input_path=$output_simulator_folder/${nb_users}_users/${nb_users}_users.input
users_topics_path=$output_simulator_folder/${nb_users}_users/${nb_users}_users_topics.csv

mkdir -p $output_folder

# Copy file provided for quick evaluation - otherwise see instructions provided
# [here](../simulator/order_crux.md) to reorder the CrUX top-list yourself (it
# takes several hours).
if [ ! -f $crux_order_traffic_path ]
then
    tar -xf crux_order_traffic.tar.gz -C $output_simulator_folder
fi

#Switch to simulator folder
cd ../simulator

if [ ! -f $users_topics_path ]
then
    # Generate users
    ./generate_users.sh $nb_users
fi

#Simulate one epoch and denoise
# Note: edit roc curve thresholds and labels in simulator.py directly
python3 simulator.py classifier $crux_classified_path $users_topics_path $output_folder

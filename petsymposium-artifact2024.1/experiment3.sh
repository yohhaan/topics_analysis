#!/bin/sh

# To completely reproduce the analysis of the paper
complete_evaluation=false

if [ "$complete_evaluation" = true ]
then
    nb_users=250000
else
    nb_users=50000
fi

output_simulator_folder=../output_web/simulator
output_folder=$output_simulator_folder/${nb_users}_users

users_input_path=$output_folder/${nb_users}_users.input
users_topics_path=$output_folder/${nb_users}_users_topics.csv

crux_order_traffic_path=.$output_simulator_folder/crux_order_traffic.csv
crux_classified_path=../output_web/crux/chrome.csv


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
    # Simulate epochs - denoise and re-identify
    python3 simulator.py denoise_and_reidentify $crux_classified_path $users_topics_path $output_folder
fi

# Plot results
python3 simulator.py plot $output_folder $nb_users
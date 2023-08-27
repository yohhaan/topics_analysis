#!/bin/sh

output_simulator_folder=../output_web/simulator
output_folder=$output_simulator_folder/classifier
crux_order_traffic_path=.$output_simulator_folder/crux_order_traffic.csv
population_size=52000

mkdir -p $output_folder

# Copy file provided for quick evaluation - otherwise see instructions provided
# [here](../simulator/order_crux.md) to reorder the CrUX top-list yourself (it
# takes several hours).
if [ ! -f $crux_order_traffic_path ]
then
    tar -xf crux_order_traffic.tar.gz -C $output_simulator_folder
fi

# generate users and simulate + plot




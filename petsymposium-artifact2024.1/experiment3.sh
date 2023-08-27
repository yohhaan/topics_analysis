#!/bin/sh

# To completely reproduce the analysis of the paper
complete_evaluation=false

output_simulator_folder=../output_web/simulator

if [ "$complete_evaluation" = true ]
then
    population_size=250000
else
    population_size=52000
fi

output_folder=$output_simulator_folder/$population_size
crux_order_traffic_path=.$output_simulator_folder/crux_order_traffic.csv

mkdir -p $output_folder

# Copy file provided for quick evaluation - otherwise see instructions provided
# [here](../simulator/order_crux.md) to reorder the CrUX top-list yourself (it
# takes several hours).
if [ ! -f $crux_order_traffic_path ]
then
    tar -xf crux_order_traffic.tar.gz -C $output_simulator_folder
fi

# generate users and simulate + plot


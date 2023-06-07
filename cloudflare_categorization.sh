#!/bin/bash
top=1000000
output_folder=output/cloudflare
domains=$output_folder/cloudflare.domains
output=$output_folder/cloudflare.csv

mkdir -p $output_folder

if [ ! -f $domains ]
then
    python3 cloudflare_api.py crux_top $top
fi

if [ ! -f $output ]
then
    source set_cloudflare_env.sh
    #Header
    python3 cloudflare_api.py cloudflare_csv_header >> $output
    #Parallel call to API with delay to be below limit of 1200 API requests per
    #5 min - 25 domains at a time - exit when 300 job have failed but wait for
    #running jobs to complete - trying to avoid gateway timeout with 10s delay
    parallel -X -N 25 --bar --delay 10 --halt soon,fail=300 -a $domains -I @@ "python3 cloudflare_api.py api_request @@ >> $output"
    #manually rerun the domain names that have failed because of API error
    #useful commands for that for future reference:
    # cat output/cloudflare/cloudflare.csv | grep error > temp
    # sed -i '/\terror/d' output/cloudflare/cloudflare.csv
fi
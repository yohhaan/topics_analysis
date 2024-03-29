#!/bin/bash
top=1000000
crux_path=../sandbox_dependencies/topics_web/crux.csv

output_folder=../output_web/cloudflare
domains=$output_folder/cloudflare_$top.domains
output=$output_folder/cloudflare.csv

mkdir -p $output_folder

if [ ! -f $domains ]
then
    python3 cloudflare_api.py crux_top $top $crux_path $domains
fi

if [ ! -f $output ]
then
    source set_cloudflare_env.sh
    #Header
    python3 cloudflare_api.py cloudflare_csv_header >> $output
    #Parallel call to API with delay to be below limit of 1200 API requests per
    #5 min - 25 domains at a time - exit when 300 jobs have failed but wait for
    #running jobs to complete - trying to avoid gateway timeout with 10s delay
    parallel -X -N 25 --bar --delay 10 --halt soon,fail=300 -a $domains -I @@ "python3 cloudflare_api.py api_request @@ >> $output"
    #manually rerun the domain names that have failed because of API error
    #useful commands for that for future reference:
    # cat output_web/cloudflare/cloudflare.csv | grep error > temp
    # sed -i '/\terror/d' output_web/cloudflare/cloudflare.csv
fi
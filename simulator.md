# Topics Simulator

For our privacy analysis, we want to quantify the risk of noise removal and
re-identification across websites associated with the Topics API. For that, we
generate users and their associated topics as described in the paper. Then,
simulate 1 or 2 advertiser(s) observing the results returned by the Topics API
during 1 or several epoch(s).

**Pre-processing CrUX: Total Ordering and Traffic Info**

We first need to set a total order on the CrUX dataset (see details in paper and
corresponding code), for that, we need to run the following command once (again
we suggest using a `screen` session): `parallel python3 sim_order_crux.py
generate ::: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15`

We use `parallel` to split the CrUX list across different processes (our machine
has 16 CPUs), each process performs the ordering in a specified range. The size
of the range is hard-coded in `sim_order_crux.py` for 16 CPUs, edit as needed.

When the `parallel` execution is over, merge results with: `python3
  sim_order_crux.py merge`


Now, we can generate users and their corresponding topics:
- Use the function `generate_parallel_input(total_nb_users)` in `sim_utils.py`
  to generate the input file that will be used by parallel in our shell script
  `./sim_generate_users.sh`
- Execute shell script `./sim_generate_users.sh` to generate a csv file
  describing the synthetic users and their top 5 topics.

Then, study the possibility of denoising and re-identifying users across
websites by 1 or 2 advertisers by simulating the Topics API for 1 or several
epochs (tested up to 30 in our privacy evaluation).

- Refer for this analysis to `simulator.py`, this script reloads the
`simulator_library` library automatically when exiting with `CTRL+D` the
interactive console so that modifications in `simulator_library.py` are taken
  into account without having to reload the simulation. Exit the interactive
  console with `exit()` when you are done.
- Refer to function `archive_main()` in `simulator.py` and corresponding
  functions mentioned there for the commands to run the analysis and plot
  results.
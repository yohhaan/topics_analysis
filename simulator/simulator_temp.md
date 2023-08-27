
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
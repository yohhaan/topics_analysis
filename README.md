# Topics Analysis: Privacy and Utility Goals

This repository contains the source code used in our privacy and utility
analysis of the [Topics API]() from the [Privacy Sandbox](). With the Topics
API, Google aims to replace third-party cookies for personalized advertising.
Find more details about our analysis in our paper [Interest-disclosing Mechanims
for Advertising are Privacy-*Exposing* (not Preserving)](https://arxiv.org/abs/2306.03825):

```bibtex
@misc{topics23_beugin,
      title={Interest-disclosing Mechanisms for Advertising are Privacy-Exposing (not Preserving)},
      author={Yohan Beugin and Patrick McDaniel},
      year={2023},
      eprint={2306.03825},
      archivePrefix={arXiv},
      primaryClass={cs.CR}
}
```

---
## Getting Started

1. Clone this [topics_analysis](https://github.com/yohhaan/topics_analysis)
   repository and the
   [sandbox_dependencies](https://github.com/yohhaan/sandbox_dependencies)
   submodule with:
   - `git clone --recurse-submodules
     git@github.com:yohhaan/topics_analysis.git` (SSH)

     or

   - `git clone --recurse-submodules
     https://github.com/yohhaan/topics_analysis.git` (HTTPS).

2. To install software dependencies, we recommend using the provided
`DockerFile` (under `.devcontainer/` for direct integration with [VS
code](https://code.visualstudio.com/docs/devcontainers/containers)).

3. Follow the steps in the `README` file of the `sandbox_dependencies` to
   manually copy into the submodule the dependencies that are not fetched
   automatically at the moment and download the rest:
    - Manual dependencies: `model.tflite`, `override_list.pb.gz` `top-1m.csv`
  `tranco_ID.csv`.
    - Download other dependencies with the `./fetch_all.sh` script in the
      submodule.

4. Automatically classify the different lists of domains considered (see
   details below).

5. Analysis of classification (see details below).

6. Perform simulation to quantify risk of noise removal and re-identification
   across websites + analysis (see details below).

Structure of the `topics_analysis` repository:
- `.devcontainer/`: folder with Dockerfile for software dependencies and
settings for [VS code Dev
containers](https://code.visualstudio.com/docs/devcontainers/containers).
- `figs/`: folder where figures are saved by the analysis.
- `output/`: folder to save several intermediary output files and processed data
  needed for future analysis.
- `sandbox_dependencies/`: git submodule pointing to another of our
  [repository](https://github.com/yohhaan/sandbox_dependencies) that contains
  some dependencies required for this project (see corresponding `README`).

---
## Topics Classification

### Manually

To classify some domains individually see `./classify_domain.sh` for the
  different options:
  - `chrome`: check in override_list (static mapping) and if not present top 5
    from ml_model (follows Colab example released by Google).
  - `ml_model_top`: run ml_model, output only top T, where T is passed as 2nd
    parameter to script.
  - `ml_model_st`: run ml_model, output categories with score >= st, where st is passed as 2nd
    parameter to script.
  - `ml_model_chrome`: run ml_model with filtering strategy used in Google Chrome Beta.
  - `ml_model_csv_header`: output csv header for ml_model_csv option.
  - `ml_model_csv`: run ml_model directly (no check against override_list and no
    filtering of output).
  - `chrome_csv_header`: output csv header for chrome_csv option.
  - `chrome_csv`: run chrome classification (first check against override list,
    if not present run ML model, and filter output of model with Chrome beta
    filtering strategy).

Pass domain names to classify as last arguments, as an example, the following
command `./classify_domain.sh chrome_csv github.com privacysandbox.com` should
output:
```
github.com      139     1
github.com      140     1
github.com      215     1
github.com      225     1
privacysandbox.com      103     0.1374019831418991
```


### Automatically (CSV output)

For our analysis of Topics, we classify several list of domains (and words from
the English dictionary). [GNU Parallel](https://www.gnu.org/software/parallel/)
is used to optimize the running time of each classification. Each list needs to
be classified only once, depending on the specs of your machine it could take a
few hours. We suggest to run each classification in a `screen` session.

We provide a shell script `process_<NAME>.sh` per classification, refer to it
for more details about the steps being executed. Here is a summary:
- `crux` and `tranco`: Top 1M most visited origins/domains from
  [CrUX](https://github.com/zakird/crux-top-lists) and
  [Tranco](https://tranco-list.eu/) classified with Topics API (static mapping
  override, ML model, chrome filtering strategy).
- `override` and `wordnet`: hostnames in override_list and English dictionary
  returned by WordNet classified with the ML model of Topics only (need raw
  output of ML model for utility analysis - we apply chrome filtering strategy
  later).

Note: the classification could probably be further optimized if we were to
figure out the Tokenizer used by Google during training and how to perform batch
inference directly with the `.tflite` model released by Google (on that last
point, one would need to take into account the label metadata file embedded in
the `.tflite` model). The `parallel` execution is sufficient for our needs.

### Analysis of Classification

- Entrypoint: `python3 analysis.py`, it reloads the `analysis_library` library
  automatically when exiting with `CTRL+D` the interactive console so that
  modifications in `analysis_library.py` are taken into account without having
  to reload each dataset (which can take time). Exit the interactive console
  with `exit()` when you are done.
- Depending on which part of the analysis you want to perform, you can refer to
  the function `archive_main()` defined in `analysis.py`; it contains references
  to how to run each part of the analysis.

---
## Chrome Filtering Verification

To verify that we filter the same way the output of the ML model than what
Google does in Google Chrome Beta, execute the following steps:

- Run `./validation_filtering.sh`, this will extract 1000 words from Wordnet and
  classify them with Topics.
- File `output/validation/validation.domains` contains the 1000 words randomly
  sampled, copy-paste this list in the input box of the Topics model shipped
  with Google Chrome Beta:
  - Install Google Chrome Beta.
  - Enable Topics features API.
  - Visit `chrome://topics-internals` to run inference.
- Run the classification in Google Chrome Beta and select the output: copy paste
  the table that is `\tab` separated in file `output/validation/validation.beta`.
- In the analysis code (`analysis.py`), uncomment the code calling the function
  `validation_parameters()` to validate parameters, it returns correct and
  incorrect domain names sets. Incorrect sets should be empty, but in practice
  there are floating point issues and so sometimes a negligeable amount of
  domains will get filtered differently. Checking the filtering strategy
  manually shows that these differences are coming from floating point
  comparison issues between our implementation and Google's. These are
  negligeable at the scale of our analysis.

---
## Cloudflare Categorization

We are interested in comparing the classification of the Topics API to the
ground truth provided by the categorization returned by [Cloudflare Domain
Intelligence
API](https://developers.cloudflare.com/api/operations/domain-intelligence-get-multiple-domain-details),
available through [Cloudflare Radar](https://radar.cloudflare.com/).

Access to the API requires the creation of a Cloudflare account to generate an
API token (with permission `Account: Intel - Read`) in order to query the Domain
Intelligence API (rate limited at about 100 monthly requests).
- Rename `set_cloudflare_env.sh.github` to `set_cloudflare_env.sh` and enter
  your `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.
- Run `cloudflare_categorization.sh` to categorize domain names with Cloudflare
  API. Some requests to the API are likely to time out, we just rerun them (see
  script for useful commands).
- Refer to the `analysis.py` code to compare Topics classification to ground
  truth provided by Cloudflare categorization. This requires beforehand to
  manually map Google's Topics to Cloudflare's categories as explained in the
  paper. We release our manual mapping in the following file
  `cloudflare_categories_manual_mapping_topics.json`.

---
## Subdomains Crafting

In our paper, we study the possibility of crafting subdomains to trigger an
untargeted or targeted classification. For that, we extract for each topic the
word from WordNet classified with most confident to that topic (see
corresponding analysis code in `analysis.py` function `utility_experiments()`).
Then, we craft for each of the top 10k most visited websites from CrUX all the
corresponding subdomains that we classify with the Topics API (see and run
`./subdomains_crafting.sh`)

---
## Topics Simulator

For our privacy analysis, we want to quantify the risk of noise removal and
re-identification across websites associated with the Topics API. For that, we
generate users and their associated topics as described in the paper. Then,
simulate 1 or 2 advertiser(s) observing the results returned by the Topics API
during 1 or several epoch(s).

### Pre-processing CrUX: Total Ordering and Traffic Info

We first need to set a total order on the CrUX dataset (see details in paper and
corresponding code), for that, we need to run the following command once (again
we suggest to use a `screen` session): `parallel python3 sim_order_crux.py
generate ::: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15`

We use `parallel` to split the CrUX list across different processes (our machine
has 16 CPUs), each process performs the ordering in a specified range. The size
of the range is hard-coded in `sim_order_crux.py` for 16 CPUs, edit as needed
(this piece of code could be optimized further but it is a one time cost only as
it is ran once).

When the `parallel` execution is over, merge results with: `python3
  sim_order_crux.py merge`


### Simulating Users - Topics API - Denoising and Re-identification

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
# Artifact Appendix

Paper title: **Interest-disclosing Mechanisms for Advertising are
Privacy-Exposing (not Preserving)**

Artifacts HotCRP Id: **#10**

Requested Badge: **Reproducible**

- [Artifact Appendix](#artifact-appendix)
  - [Description](#description)
    - [Security/Privacy Issues and Ethical Concerns](#securityprivacy-issues-and-ethical-concerns)
  - [Basic Requirements](#basic-requirements)
    - [Hardware Requirements](#hardware-requirements)
    - [Software Requirements](#software-requirements)
    - [Estimated Time and Storage Consumption](#estimated-time-and-storage-consumption)
  - [Environment](#environment)
    - [Accessibility](#accessibility)
    - [Set up the environment](#set-up-the-environment)
    - [Testing the Environment](#testing-the-environment)
  - [Artifact Evaluation](#artifact-evaluation)
    - [Main Results and Claims](#main-results-and-claims)
      - [Main Result 1: The distribution of observed topics on the web is skewed](#main-result-1-the-distribution-of-observed-topics-on-the-web-is-skewed)
      - [Main Result 2: Noisy topics can be removed by advertisers](#main-result-2-noisy-topics-can-be-removed-by-advertisers)
      - [Main Result 3: Users can be re-identified across websites](#main-result-3-users-can-be-re-identified-across-websites)
      - [Main Result 4: The ML model outputs topics in common with the ground truth](#main-result-4-the-ml-model-outputs-topics-in-common-with-the-ground-truth)
      - [Main Result 5: Publishers can influence the classification of their websites](#main-result-5-publishers-can-influence-the-classification-of-their-websites)
    - [Experiments](#experiments)
      - [Experiment 1: Domains classification by the Topics API](#experiment-1-domains-classification-by-the-topics-api)
      - [Experiment 2: Noise Removal](#experiment-2-noise-removal)
      - [Experiment 3: Collusion and Cross-site Tracking](#experiment-3-collusion-and-cross-site-tracking)
      - [Experiment 4: Static Mapping Reclassification](#experiment-4-static-mapping-reclassification)
      - [Experiment 5: Crafting Subdomains](#experiment-5-crafting-subdomains)
  - [Limitations](#limitations)
  - [Notes on Reusability](#notes-on-reusability)


## Description

This artifact contains all of our analysis code used in our paper to evaluate
the privacy and utility objectives of the Topics API for the Web.

Our artifact allows to:
- Classify domains into topics with the Topics API.
- Generate arbitrarly large populations of synthetic users.
- Simulate the Topics API results observed by advertisers
- Evaluate if the noisy topics returned by the API can be flagged and discarded.
- Evaluate if users can be re-identified across websites and epochs.
- Measure the accuracy of the classification performed by the Topics API
  (compare to ground truth for static mapping, manual verification, and
  comparison to Cloudflare categorization)
- Craft millions of subdomains and evaluate if the Topics API classification can
  be influenced.
- Reproduce the results and analysis from our paper.

### Security/Privacy Issues and Ethical Concerns

The only privacy issue that could appear would be when manually verifying the
accuracy of the classification of the Topics API. This requires to automatically
pull the meta description of a sample of websites drawn randomly from a top 1M
top-list. As such, the sensitivity of the content (adult-only, etc.) of these
websites can not be guaranteed and we recommend using a secure VPN to hide the
requests from your ISP and your IP from these websites. As this manual
verification is also time-consuming, we do not expect artifact reviewers to
perform it.

## Basic Requirements

### Hardware Requirements

- No specific hardware required except for an x86 machine.
- But a machine with at least 8 cores/16 threads and 64GB of RAM is recommended
  to run things quicker.

### Software Requirements

- [`docker`](https://www.docker.com/products/docker-desktop) is required.
- Use of [`screen`](https://www.gnu.org/software/screen/) is recommended.
- Follow provided instructions to install and fetch other dependencies.

### Estimated Time and Storage Consumption

Our analysis can be quite lengthy to fully replicate: from several hours to
parse the millions of crafted subdomains to several days to classify the top 1M
most visited websites with Cloudflare API.

And so, while we provide the explanations to run all of our experiments, we do
not expect artifact reviewers to execute the most time-consuming ones. Instead,
we provide parameters and scripts that allow for a quick evaluation of the main
features of our artifact.

- Time: about 1h30 for the quick evaluation with 8 cores/16 threads/64GB RAM.
- Storage: 2GB of free storage should be sufficient for the quick evaluation.


## Environment

### Accessibility

Our artifact is accessible through this GitHub repository:
https://github.com/yohhaan/topics_analysis. When cloning it with the command
provided below and in our `README.md` file, you will also clone the following
repository https://github.com/yohhaan/sandbox_dependencies as a git submodule.
For future stable reference, we have created a `petsymposium-artifact2024.1` tag
on these 2 repositories.


### Set up the environment

1. Clone this [topics_analysis](https://github.com/yohhaan/topics_analysis)
   repository and the
   [sandbox_dependencies](https://github.com/yohhaan/sandbox_dependencies)
   submodule at once with:
   - `git clone --recurse-submodules git@github.com:yohhaan/topics_analysis.git`
     (SSH)
   - `git clone --recurse-submodules
     https://github.com/yohhaan/topics_analysis.git` (HTTPS)

A `Dockerfile` is provided under `.devcontainer/` (for direct integration with
[VS Code](https://gist.github.com/yohhaan/b492e165b77a84d9f8299038d21ae2c9)). To
manually build the image and deploy the Docker container, follow the
instructions below:

**Requirement:** [`docker`](https://www.docker.com/products/docker-desktop)

2. Build the Docker image:
```sh
docker build -t topics_analysis .devcontainer/
```

3. Deploy a Docker container:
```sh
docker run --rm -it -v ${PWD}:/workspaces/topics_analysis \
    -w /workspaces/topics_analysis \
    --entrypoint bash topics_analysis:latest
```

**Note:** some commands to reproduce our results may take a long time to execute
depending on the amount of resources of your machine. We recommend running the
above command to deploy a Docker container in a
[`screen`](https://www.gnu.org/software/screen/) session that you can then
detach and re-attach to your terminal as needed.

4. Fetch the required Privacy Sandbox dependencies:
```
cd sandbox_dependencies
./fetch_all.sh
cd ..
```

### Testing the Environment

Verify that you obtain the same output when classifying the following 3 domains:

```
./classify.sh chrome_csv github.com privacysandbox.com petsymposium.org

INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
github.com      139     1
github.com      140     1
github.com      215     1
github.com      225     1
privacysandbox.com      103     0.13740....
petsymposium.org        236     0.56497....
petsymposium.org        238     0.44849....
```

## Artifact Evaluation

### Main Results and Claims

#### Main Result 1: The distribution of observed topics on the web is skewed
- The classification of top lists of domains show that the distribution of
topics is very non-uniform: some topics are observed on a lot of websites while
some can be never observed at all.
- See section 4.4 and paragraph "Topics Distribution as a Prior." in our paper
  (Figure 3 (a), (b), and (c)).
- See [Experiment 1: Domains classification by the Topics
  API](#experiment-1-domains-classification-by-the-topics-api).

#### Main Result 2: Noisy topics can be removed by advertisers
- We can build a classifier that considers topics observed very rarely on the
  top lists as noisy.
- Advertisers who observe across time topics returned by each user can identify
  the ones that are more likely to be genuine than noisy.
- See section 4.4 "No Collusion and Noise Removal" and paragraphs "One-shot
  Scenario." and "Multi-shot Scenario." (Table 4 and Figure 4 (a), (b), and
  (c)).
- See [Experiment 2: Noise Removal](#experiment-2-noise-removal).
- See [Experiment 3: Collusion and Cross-site
  Tracking](#experiment-3-collusion-and-cross-site-tracking).

#### Main Result 3: Users can be re-identified across websites
- Advertisers can uniquely and with a higher chance than random re-identify
  across websites a portion of the users with stable interests.
- Across time, advertisers re-identify a higher portion of the simulated users.
- See section 4.5 "Collusion and Cross-site Tracking" (Figure 5).
- See [Experiment 3: Collusion and Cross-site
  Tracking](#experiment-3-collusion-and-cross-site-tracking).

#### Main Result 4: The ML model outputs topics in common with the ground truth
- The Topics model outputs at least one topic in common with the ground truth on
  65% of the domains from the static mapping.
- See section 5.1 "Static Mapping Reclassification".
- See [Experiment 4: Static Mapping
  Reclassification](#experiment-4-static-mapping-reclassification).

#### Main Result 5: Publishers can influence the classification of their websites
- Website operators can influence their site tagging by the Topics API.
- See section 5.3 "Crafting Subdomains" (Figure 6).
- See [Experiment 5: Crafting Subdomains](#experiment-5-crafting-subdomains).

### Experiments

**Note:** Shell scripts `./experiment{1/3/5}.sh` contains the variable
`complete_evaluation` that needs to be set to `true` if you are looking to fully
reproduce our results (we recommend leaving it set to `false` for a quick
evaluation of our artifact).


#### Experiment 1: Domains classification by the Topics API
- Time to execute: about 30 min (quick evaluation) | 1h+ (complete evaluation)
- Disk space: about 150MB (quick evaluation) | about 1.2GB (complete evaluation)
- Result or claim: [Main Result 1: The distribution of observed topics on the
  web is
  skewed](#main-result-1-the-distribution-of-observed-topics-on-the-web-is-skewed)

Run `./experiment1.sh` to classify the following lists of domains and words from
the English dictionary into their corresponding topics:
- `crux` (quick evaluation): Top 1M most visited origins/domains from
  [CrUX](https://github.com/zakird/crux-top-lists)
- `tranco` (complete evaluation): Top 1M most visited origins/domains from
  [Tranco](https://tranco-list.eu/)
- `wordnet` (complete evaluation): English dictionary returned by WordNet

Results: see `output_web/crux`, `output_web/tranco`, and `output_web/wordnet`
for the classification (`csv` files), figures, and statistics. This experiment
also extracts some statistics about the static mapping annotated by Google in
the `output_web/static` folder. The `cdf_histplot_domains_per_topic.pdf` figures
correspond to Figures 3 (a), (b), and (c) from our paper.

#### Experiment 2: Noise Removal
- Prerequisite: run experiment 1 (quick evaluation)
- Optional prerequisite: re-order CrUX which takes several hours (optional)
- Time to execute: about 2 min
- Disk space: about 50MB
- Result or claim: [Main Result 2: Noisy topics can be removed by
  advertisers](#main-result-2-noisy-topics-can-be-removed-by-advertisers)

Run `./experiment2.sh` to simulate a population of synthetic users reporting
their topics across epochs to an advertiser identifying the noisy topics to
discard them.

The generation of synthetic users requires to set a total order on the CrUX
top-list, for a quick evaluation, we provide such ordered list with our
artifact. See instructions provided [here](../simulator/order_crux.md) to
reorder the CrUX top-list yourself (it takes several hours).

Results: see `output_web/simulator/classifier/` for results about the classifier
(Table 4 of our paper corresponds to `denoise_one_shot.stats`). To obtain graphs
from Figure 4 of our paper, see [Experiment 3: Collusion and Cross-site
  Tracking](#experiment-3-collusion-and-cross-site-tracking).

Note: results can slightly differ depending on the generated population (for
instance `petsymposium-artifact2024.1/52000_users_topics.csv.tar.gz` is one of
the populations we generated for our results).

#### Experiment 3: Collusion and Cross-site Tracking
- Prerequisite: run experiment 1 (quick evaluation)
- Optional prerequisite: re-order CrUX which takes several hours (optional)
- Time to execute: about 15 min (quick evaluation) | about 6h15min (complete
evaluation)
- Disk space: about 60MB (quick evaluation) | about 110MB (complete
evaluation)
- Result or claim: [Main Result 2: Noisy topics can be removed by
  advertisers](#main-result-2-noisy-topics-can-be-removed-by-advertisers)
 and [Main Result 3: Users can be re-identified across
  websites](#main-result-3-users-can-be-re-identified-across-websites)

Run `./experiment3.sh` to simulate a population of synthetic users across epochs
and evaluate how two advertisers observing the topics of these users can
re-identify them across websites.

The generation of synthetic users requires to set a total order on the CrUX
top-list, for a quick evaluation, we provide such ordered list with our
artifact. See instructions provided [here](../simulator/order_crux.md) to
reorder the CrUX top-list yourself (it takes several hours).

Population Size:
- 50k users (quick evaluation)
- 250k users (complete evaluation)

Results: see under `output_web/simulator/` the folder corresponding to the
population size you simulated for results (`denoise_multi_shot.stats` and
`cdf_reidentification.stats`). Figures 4 of paper correspond to
`denoise_accuracy_precision.pdf`, `denoise_tpr_fpr.pdf`,
`denoise_nb_top5_recovered`. Figure 5 of paper corresponds to
`cdf_size_groups.pdf`

Note: you need to run the complete evaluation to get more meaningful results
(larger population size), the results may slightly differ depending on the
generated population (for instance
`petsymposium-artifact2024.1/250000_users_topics.csv.tar.gz` is one of the
populations we generated for our results).

#### Experiment 4: Static Mapping Reclassification
- Time to execute: about 15 min
- Disk space: less than 3MB (negligible)
- Result or claim: [Main Result 4: The ML model outputs topics in common with
  the ground
  truth](#main-result-4-the-ml-model-outputs-topics-in-common-with-the-ground-truth)

Run `./experiment4.sh` to compare the ML classification of the domains in the
static mapping to the manual annotations from Google. The script first
classifies the domains from the static mapping provided by Google (override_list
  classified into `output_web/override`).

Results: see folder `output_web/override` for the results about the comparison
for both the two filtering strategies discussed in the paper:
`same_nb_as_static_comparison_stats.txt` and
`chrome_filtering_comparison_stats.txt`. They can directly be compared to the
results in Table 5 of our paper.

#### Experiment 5: Crafting Subdomains
- Prerequisite: run experiment 1 (quick evaluation)
- Time to execute: about 2 min (quick evaluation) | about 2h15 (complete
evaluation)
- Disk space: about 10MB (quick evaluation) | about 850MB (complete
evaluation)
- Result or claim: [Main Result 5: Publishers can influence the classification
  of their
  websites](#main-result-5-publishers-can-influence-the-classification-of-their-websites)

Run `./experiment5.sh` to craft subdomains and evaluate the possibility of
triggering an untargeted or targeted classification. For that, we extract for
each topic the word from WordNet classified with most confidence to that topic,
and craft for each of the top most visited websites from CrUX all the
corresponding subdomains quick evaluatiothat we classify with the Topics API.
This results in 350 topics x 100 (quick evaluation) /or/ 10000 (complete
evaluation) websites = 35k (quick evaluation) /or/ 3.5M (complete evaluation)
subdomains total.

The script automatically detects if WordNet was classified during experiment 1
(complete evaluation). If so, we can extract the list of top word for each
topic, if not (quicker evaluation), we use the provided file
`petsymposium-artifact2024.1/taxonomy.words`.

Results: see folder `output_web/crafted_subdomains_{100/or/10000}` for the
results of the classification of these crafted subdomain:
`targeted_untargeted_stats.txt` and `targeted_untargeted_success.pdf`. You
should get a simular figure to Figure 6 from our paper (to replicate it, you
need to run the complete evaluation).

## Limitations

Google did not clearly specify how they were filtering the output of the model
used in Topics API, but we found it by looking through Chromium source code. To
validate that our filtering was matching Google Chrome's implementation, we
compared both output classifications on thousands of random domains and words.
Since the submission of our paper, Google released a new taxonomy and model for
the Topics API in Google Chrome. Thus, to perform this validation today, the
versions used in this analysis would need to be updated to the most recent ones,
another less likely option would be to have access to an older version of Google
Chrome Beta. See the corresponding [code and
documentation](../validation_filtering/) for more details.

Manually verifying the assignment of a random sample of websites to topics
(section 5.2 in the paper) requires the use of a VPN (see [Security/Privacy
Issues and Ethical Concerns](#securityprivacy-issues-and-ethical-concerns)) and
is quite a time-consuming process. For completeness, the code is provided
[here](../manual_verification/).

Finally, the categorization of the top 1M websites (section 5.2 and Table 6 in
the paper) through the Cloudflare Domain Intelligence API required us several
days to completely process. Given that only a very limited number of requests
can normally be issued per month to this specific API, and that we were able to
obtain an exception from Cloudflare, it would be impossible to reproduce these
results in a reasonable time. Again for completeness, we provide the code, see
the corresponding [documentation
file](../cloudflare_categorization/cloudflare_categorization.md) for more
details.

## Notes on Reusability

This artifact can be reused for future analyses of the Topics API and other
Privacy Sandbox APIs. For instance, different lists of domain names can be
classified by adapting the existing scripts, new model versions and taxonomies
can be evaluated by adding them to the git submodule, and other scenarios can be
tested by modifying some code base. Indeed, we are actively working on such
extensions of our work.

To simulate the Topics API, we generate synthetic browsing histories drawn
directly from aggregated distributions published by researchers who collaborated
with [Mozilla](https://www.usenix.org/conference/soups2020/presentation/bird)
and [Google](https://dl.acm.org/doi/10.1145/3517745.3561418). Our approach not
only does not require that researchers collect real browsing histories (which
creates bias and ethical issues) but also enables reproducible methodologies and
the generation of publicly sharable synthetic datasets. As a result, other
methodologies requiring the use of browsing history could benefit from adopting
our approach. Please reach out if you have such use cases.

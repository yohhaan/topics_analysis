# Artifact Appendix

Paper title: **Interest-disclosing Mechanisms for Advertising are
Privacy-Exposing (not Preserving)**

Artifacts HotCRP Id: **#10**

Requested Badge: **Reproducible**

## Description

This artifact contains all of our analysis code used in our paper to evaluate
the privacy and utility objectives of the Topics API for the Web.

Our artifact allows to:
- Classify domains into topics, exactly as the Topics API implemented in Google
  Chrome Beta would.
- Generate populations of any size of synthetic users with stable interests.
- Simulate what the Topics API would return to advertisers that observe these
  synthetic users across several epochs.
- Evaluate how advertisers can flag and discard the noisy topics returned by the
  API and re-identify users across different websites and epochs.
- Evaluate how accurate the classification of the Topics API model is on the 10k
  domains from the static mapping released by Google.
- Perform a manual verification of the assignment of a random sample of domains
  into topics.
- Classify domains with the Cloudflare Domain Intelligence API and compare
  Topics API's categorization with the one from Cloudflare.
- Craft millions of subdomains and evaluate the possibility to abuse the Topics
  API's classification.
- Reproduce the results and graphs from our corresponding paper.


### Security/Privacy Issues and Ethical Concerns

Manually performing the verification of the assignment of a random sample of
domains into topics requires our script to automatically pull the meta
descriptions of the associated websites. We recommend using a secure VPN to hide
the requests being made from your ISP and hide your IP from these random
websites: the sensitivity of their content can not be guaranteed as they are
randomly drawn from a 1M top-list. For this reason and because this manual
verification is time-consuming, we do not expect artifact reviewers to perform
such experiment.


## Basic Requirements

### Hardware Requirements

- No specific hardware required.
- But a machine with at least 8 cores/16 threads and 64GB of RAM is recommended
  to run things quicker.

### Software Requirements

- [`docker`](https://www.docker.com/products/docker-desktop) is required.
- Use of [`screen`](https://www.gnu.org/software/screen/) is recommended.
- Follow provided instructions to install and fetch other dependencies.

### Estimated Time and Storage Consumption

We do not expect artifact reviewers to attempt to fully reproduce our analysis,
as this could take several days from scratch. Instead, we specify parameters
that allow for a quicker evaluation of our artifact along with the ones used for
the complete analysis in the paper.

- Time: about 2h for the quick evaluation with 8 cores/16 threads/64GB RAM.
- Storage: 10GB of free storage should be largely sufficient.


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
privacysandbox.com      103     0.1374019831418991
petsymposium.org        236     0.5649784803390503
petsymposium.org        238     0.4484950006008148
```

## Artifact Evaluation

### Main Results and Claims

#### Main Result 1: The distribution of observed topics on the web is skewed
- The classification of top lists of domains show that the distribution of
topics is very non-uniform: some topics are observed on a lot of websites while
some can be never observed at all.
- See section 4.2 and paragraph "Topics Distribution as a Prior." in our paper
  (Figure 3 (a), (b), and (c)).
- See [Experiment 1: Domains classification by the Topics
  API](#experiment-1-domains-classification-by-the-topics-api).

#### Main Result 2: Noisy topics can be removed by advertisers
- We can build a classifier that considers topics observed very rarely on the
  top lists as noisy.
- Advertisers who observe across time topics returned by each user can identify
  the ones that are more likely to be genuine than noisy.
- See section 4.2 "No Collusion and Noise Removal" and paragraphs "One-shot
  Scenario." and "Multi-shot Scenario." (Table 3 and Figure 4 (a), (b), and
  (c)).
- See [Experiment 2: Noise Removal](#experiment-2-noise-removal).

#### Main Result 3: Users can be re-identified across websites
- Advertisers can uniquely and with a higher chance than random re-identify
  across websites a portion of the users with stable interests.
- Across time, advertisers re-identify a higher portion of the simulated users.
- See section 4.3 "Collusion and Cross-site Tracking" (Figure 5).
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

**Note:** Shell scripts `./experiment{1/2/3/5}.sh` contains the variable
`longer_evaluation` that needs to be set to `true` if you are looking to fully
reproduce our results (we recommend leaving it set to `false` for a way quicker
evaluation).


#### Experiment 1: Domains classification by the Topics API
- Time to execute: about 30 min for the quick evaluation | 4h+ for longer one
- Disk space: about 2GB
- Result or claim: [Main Result 1: The distribution of observed topics on the
  web is
  skewed](#main-result-1-the-distribution-of-observed-topics-on-the-web-is-skewed)

Run `./experiment1.sh` to classify the following lists of domains and words from
the English dictionary into their corresponding topics:

- `override` (quick evaluation): domains from the override_list (Static mapping
  provided by Google)
- `crux` (quick evaluation): Top 1M most visited origins/domains from
  [CrUX](https://github.com/zakird/crux-top-lists)
- `tranco` (longer evaluation): Top 1M most visited origins/domains from
  [Tranco](https://tranco-list.eu/)
- `wordnet` (longer evaluation): English dictionary returned by WordNet

Results: the results of the classifications are stored under the `output/`
folder, figures and statistics under the `figs/` folder. Note that figures will
likely be slightly different from the ones from the paper as you downloaded a
newer version of the sandbox dependencies (top lists) than when originally ran.

#### Experiment 2: Noise Removal
- Prerequisite: run experiment 1 (quick evaluation)
- Time to execute: about 30 min
- Disk space: about 3GB
- Result or claim: [Main Result 2: Noisy topics can be removed by
  advertisers](#main-result-2-noisy-topics-can-be-removed-by-advertisers)

We are in the process of finalizing the transfer of this part of our code base
to a more modular script to facilitate reproduction. In the meantime, follow
instructions in this documentation file [../simulator.md](../simulator.md).

#### Experiment 3: Collusion and Cross-site Tracking
- Prerequisite: run experiment 1 (quick evaluation)
- Time to execute: about 30 min
- Disk space: about 5GB
- Result or claim: [Main Result 3: Users can be re-identified across
  websites](#main-result-3-users-can-be-re-identified-across-websites)

We are in the process of finalizing the trasnfer of this part of our code base
to a more modular script to facilitate reproduction. In the meantime, follow
instructions in this documentation file [../simulator.md](../simulator.md).

#### Experiment 4: Static Mapping Reclassification
- Prerequisite: run experiment 1 (quick evaluation)
- Time to execute: about 15 min (quick evaluation only)
- Disk space: negligible
- Result or claim: [Main Result 4: The ML model outputs topics in common with
  the ground
  truth](#main-result-4-the-ml-model-outputs-topics-in-common-with-the-ground-truth)

Run `./experiment4.sh` to compare the ML classification of the domains in the
static mapping to the manual annotations from Google. 

Results: the statistics (`chrome_comparison_stats.txt` and
`same_nb_as_o_comparison_stats.txt`) will be saved to the `output/override`
folder, they can directly be compared to the results in Table 4 of our paper.

#### Experiment 5: Crafting Subdomains
- Prerequisite: run experiment 1 (quick evaluation)
- Time to execute: about 3 min for the quick evaluation | 2h+ for longer one
- Disk space: about 50MB
- Result or claim: [Main Result 5: Publishers can influence the classification
  of their
  websites](#main-result-5-publishers-can-influence-the-classification-of-their-websites)

Run `./experiment5.sh` to craft subdomains and evaluate the possibility of
triggering an untargeted or targeted classification. For that, we extract for
each topic the word from WordNet classified with most confidence to that topic,
and craft for each of the top most visited websites from CrUX all the
corresponding subdomains that we classify with the Topics API.

For a quick evaluation, we provide the list `taxonomy.words` of top word for
each topic, otherwise, experiment 1 must be run in longer evaluation mode to
classify WordNet.

Results: a figure similar to Figure 6 from our paper is saved at the following
path: `figs/subdomains/words_targeted_untargeted_success.pdf`.


## Limitations

Google released a new taxonomy and model for the Topics API for the Web after
the submission of our paper. Thus, the latest version of Google Chrome Beta can
not be used anymore to validate (as it used to be the case) that our filtering
is the same as Google Chrome's on the versions of the model and taxonomy used in
our paper. An older version of Google Chrome Beta or updating the sandbox
dependencies would be required. See also the corresponding [documentation
file](../validation_filtering.md) for more details.

Manually verifying the assignment of a random sample of websites to topics
(section 5.2 in the paper) requires the use of a VPN (see [Security/Privacy
Issues and Ethical Concerns](#securityprivacy-issues-and-ethical-concerns)) and
is quite a time-consuming process. The code is still provided for completeness
(see the `utility_experiments()` function in `analysis.py` if you are
interested).

Finally, the categorization of the top 1M websites (section 5.2 and Table 5 in
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
the generation of publicly sharable synthetic datasets. Thus, other
methodologies requiring the use of browsing history could benefit from adopting
our approach. Please reach out if you have such use cases.
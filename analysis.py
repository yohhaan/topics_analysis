import config
import dependencies
import analysis_library
import utils

import code
import importlib
import os
import numpy as np
import pandas as pd
import re


# PATHS
chrome = "_chrome"
csv = ".csv"
#
fig_paths = [
    f"figs/",
    f"figs/crux",
    f"figs/o",
    f"figs/override",
    f"figs/tranco",
    f"figs/wordnet",
    f"figs/subdomains",
]
override = "output/override/override"
crux = "output/crux/crux"
tranco = "output/tranco/tranco"
wordnet = "output/wordnet/wordnet"
cloudflare = "output/cloudflare/cloudflare"
topics_subdomains = "output/subdomains/topics_subdomains"
words_subdomains = "output/subdomains/words_subdomains"
#
override_csv = override + csv
override_chrome_csv = override + chrome + csv
#
crux_chrome_csv = crux + chrome + csv
#
tranco_chrome_csv = tranco + chrome + csv
#
wordnet_csv = wordnet + csv
wordnet_chrome_csv = wordnet + chrome + csv
#
cloudflare_csv = cloudflare + csv
#
topics_subdomains_chrome_csv = topics_subdomains + csv
words_subdomains_chrome_csv = words_subdomains + csv
topics_targeted_csv = topics_subdomains + "_targeted" + csv
words_targeted_csv = words_subdomains + "_targeted" + csv


def check_create_paths():
    for path in fig_paths:
        os.makedirs(path, exist_ok=True)


def override_create_df():
    """
    Create Pandas Dataframe of override list
    """
    domains = []
    topics = []
    scores = []
    for entry in config.override_list.entries:
        # extract topic ids manually classified
        ids = entry.topics.topic_ids
        if ids == []:
            # empty
            domains.append(entry.domain)
            topics.append(-2)  # -2 means unknown/no topic id, likely sensitive
            scores.append(1)  # manually annotated
        else:
            for id in ids:
                domains.append(entry.domain)
                topics.append(id)
                scores.append(1)  # manually annotated, we assume score equal to 1
    df_override = pd.DataFrame({"domain": domains, "topic_id": topics, "score": scores})
    return df_override


def read_classified_csv(filename):
    """
    Read csv classified by model (with output for 350 topics)
    """
    # specify name of columns
    df = pd.read_csv(filename, sep="\t")
    column_names = df.columns
    df_unpivot = pd.melt(df, id_vars="domain", value_vars=column_names[1:])
    df_unpivot.columns = ["domain", "topic_id", "score"]
    df_unpivot["topic_id"] = df_unpivot["topic_id"].astype("int")
    return df_unpivot


def read_chrome_csv(filename):
    """
    Read csv classified by model with chrome filtering strategy already applied
    """
    return pd.read_csv(
        filename,
        sep="\t",
        usecols=[1, 2, 3],  # discard index column
        dtype={"domain": str, "topic_id": int, "score": float},
    )


def validation_parameters():
    """
    After running the ./validation_filtering.sh script, and having classified the
    words used in the validation by Chrome Beta on chrome://topics-internals,
    run this to get a list of correct/incorrect output
    """
    output_folder = "output/validation/"
    validation_chrome_path = output_folder + "validation_chrome.csv"
    validation_beta_path = output_folder + "validation.beta"
    correct = []
    incorrect = []
    if not (os.path.isfile(validation_chrome_path)) or not (
        os.path.isfile(validation_beta_path)
    ):
        print(
            "Error file does not exist, have you run the shell script first and created validation.beta?"
        )
        return
    else:
        df_validation_chrome = pd.read_csv(validation_chrome_path, sep="\t")

    with open(validation_beta_path, "r") as f:
        beta = f.readlines()
    import re

    for line in beta:
        domain, labels = line.split("\t")
        ids_beta = [int(id) for id in re.findall(r"\b\d+\b", labels)]
        if ids_beta == []:
            ids_beta = [-2]
        ids_model = df_validation_chrome[df_validation_chrome["domain"] == domain][
            "topic_id"
        ]
        intersection = list(set(ids_model).intersection(ids_beta))
        if len(ids_beta) == len(intersection):
            correct.append(domain)
        else:
            incorrect.append(domain)
    return correct, incorrect


def chrome_filtering():
    """
    Run this once after classification to be able to perform analysis
    Note: we have to run it on override and wordnet because we could not do it
    at inference time (needed all results for utility section) contrary to
    Tranco and CrUX
    """
    # Apply Chrome Filtering - run this once !
    df_override = read_classified_csv(override_csv)
    df_override_chrome = analysis_library.chrome_filter(
        df_override, override_chrome_csv
    )

    df_wordnet = read_classified_csv(wordnet_csv)
    df_wordnet_chrome = analysis_library.chrome_filter(df_wordnet, wordnet_chrome_csv)


def describe_all():
    df_crux_chrome = pd.read_csv(crux_chrome_csv, sep="\t")
    analysis_library.graph_describe_all(df_crux_chrome, "crux", "chrome")

    df_o = override_create_df()
    analysis_library.graph_describe_all(df_o, "o", "o")

    df_override_chrome = read_chrome_csv(override_chrome_csv)
    analysis_library.graph_describe_all(df_override_chrome, "override", "chrome")

    df_tranco_chrome = pd.read_csv(tranco_chrome_csv, sep="\t")
    analysis_library.graph_describe_all(df_tranco_chrome, "tranco", "chrome")

    df_wordnet_chrome = read_chrome_csv(wordnet_chrome_csv)
    analysis_library.graph_describe_all(df_wordnet_chrome, "wordnet", "chrome")


def utility_experiments():
    # Experiment 1
    # Compare model performance on override list
    df_o = override_create_df()

    # Model Classified Override List - same top nb of topics as in o
    df_override = read_classified_csv(override_csv)
    analysis_library.compare_to_ground_truth(
        df_o, df_override, "override", "same_nb_as_o", True
    )
    analysis_library.results_model_ground_truth(
        df_o, "override", "same_nb_as_o", True, False
    )

    # Model Classified Override List - chrome filter
    df_override_chrome = read_chrome_csv(override_chrome_csv)
    analysis_library.compare_to_ground_truth(
        df_o, df_override_chrome, "override", "chrome", False
    )
    analysis_library.results_model_ground_truth(df_o, "override", "chrome", True, False)

    # Experiment 2
    # manual verification
    # extract top 385
    df_crux_chrome = pd.read_csv(crux_chrome_csv, sep="\t")
    analysis_library.crux_extract_sample_size_x(df_crux_chrome, 385, "crux", "exp2")
    # /!\ WARNING /!\
    # Following call make http requests to random websites, you may want to use
    # a VPN for that
    analysis_library.crux_augment_with_meta_description("crux", "exp2")
    # manual verification
    analysis_library.crux_verification("crux", "exp2")

    # Cloudflare comparison
    # Need manual mapping of topics
    analysis_library.parse_cloudflare_topics_mapping()

    # compare manual mapping - override list
    df_o = override_create_df()
    df_cloudflare = pd.read_csv(cloudflare_csv, sep="\t")
    df_cloudflare["domain"] = df_cloudflare["domain"].apply(
        lambda x: re.sub(r"[^a-zA-Z0-9]+", " ", x)
    )
    df_c = pd.merge(df_o, df_cloudflare, on="domain", how="inner")
    analysis_library.compare_topics_to_cloudflare(df_o, df_c, "override")
    analysis_library.describe_results_cloudflare_comparison("override")

    # Compare crux
    df_crux_chrome = pd.read_csv(crux_chrome_csv, sep="\t")
    df_cloudflare = pd.read_csv(cloudflare_csv, sep="\t")
    analysis_library.compare_topics_to_cloudflare(
        df_crux_chrome, df_cloudflare, "1M", True
    )
    for r in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
        analysis_library.describe_results_cloudflare_comparison("1M", r)

    # Experiment 3
    df_wordnet = read_classified_csv(wordnet_csv)
    # extract top word for each topic ordered by topic id : first word = unknown topic
    top = 1
    df_extract = (
        df_wordnet.sort_values("score", ascending=False).groupby("topic_id").head(top)
    )
    df_extract.drop("score", axis=1, inplace=True)
    df_temp = df_extract.sort_values("topic_id")
    df_temp.drop("topic_id", axis=1, inplace=True)
    df_temp.to_csv(
        "output/subdomains/taxonomy.words",
        sep="\t",
        index=False,
        header=False,
    )

    # Now go run `./subdomains_crafting.sh`

    # After run is over, use following commands:
    analysis_library.words_crafted_subdomains(
        crux_chrome_csv, words_subdomains_chrome_csv, words_targeted_csv
    )
    analysis_library.plot_crafted_subdomains("output/subdomains/words_results.csv")


def archive_main():
    """
    Archive of the commands to put in main to replicate results in paper
    """
    # Validation Chrome Filtering Parameters - manually inspect incorrect array
    # after, ideally len(incorrect) == 0 but floating point issues
    correct, incorrect = validation_parameters()

    # Filter the raw model output according to Google Filtering Strategy
    chrome_filtering()

    # Display Stats for the different datasets
    describe_all()
    # And taxonomy
    analysis_library.taxonomy()

    # Utility
    utility_experiments()


def main():
    """
    Main function for analysis and figs
    """
    check_create_paths()
    dependencies.load_all()

    # refer to archive_main() and corresponding functions mentioned there for
    # the commands to run the analysis

    while True:
        try:
            importlib.reload(analysis_library)
        except Exception as e:
            print("WARNING: EXCEPTION:", e)
        # Interactive console (exit with `exit()`)
        code.interact(local=dict(globals(), **locals()))


if __name__ == "__main__":
    main()

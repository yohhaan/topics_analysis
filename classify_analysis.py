import config
import dependencies
import analysis_library

import numpy as np
import os
import pandas as pd
import sys

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


def check_create_paths():
    for path in fig_paths:
        os.makedirs(path, exist_ok=True)


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


def override_create_df():
    """
    Create Pandas Dataframe of override list
    """
    domains = []
    topics = []
    scores = []
    for entry in config.web_override_list.entries:
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


if __name__ == "__main__":
    check_create_paths()
    dependencies.load_all()

    if sys.argv[1] == "override":
        # Need to filter output of ML model if file does not exist already
        if not (os.path.isfile(override_chrome_csv)):
            df_override = read_classified_csv(override_csv)
            df_override_chrome = analysis_library.chrome_filter(
                df_override, override_chrome_csv
            )
        # Plot graphs in figs/ folder and extract stats
        df_override_chrome = read_chrome_csv(override_chrome_csv)
        analysis_library.graph_describe_all(df_override_chrome, "override", "chrome")

    elif sys.argv[1] == "crux":
        # Plot graphs in figs/ folder and extract stats
        df_crux_chrome = pd.read_csv(crux_chrome_csv, sep="\t")
        analysis_library.graph_describe_all(df_crux_chrome, "crux", "chrome")

    elif sys.argv[1] == "tranco":
        # Plot graphs in figs/ folder and extract stats
        df_tranco_chrome = pd.read_csv(tranco_chrome_csv, sep="\t")
        analysis_library.graph_describe_all(df_tranco_chrome, "tranco", "chrome")

    elif sys.argv[1] == "wordnet":
        # Need to filter output of ML model if file does not exist already
        if not (os.path.isfile(wordnet_chrome_csv)):
            df_wordnet = read_classified_csv(wordnet_csv)
            df_wordnet_chrome = analysis_library.chrome_filter(
                df_wordnet, wordnet_chrome_csv
            )
        # Plot graphs in figs/ folder and extract stats
        df_wordnet_chrome = read_chrome_csv(wordnet_chrome_csv)
        analysis_library.graph_describe_all(df_wordnet_chrome, "wordnet", "chrome")

    elif sys.argv[1] == "override_compare":
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
        analysis_library.results_model_ground_truth(
            df_o, "override", "chrome", True, False
        )

    else:
        raise ValueError("Incorrect argument passed to the function")

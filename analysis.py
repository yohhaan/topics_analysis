import config
import dependencies
import analysis_library

import code
import importlib
import os
import pandas as pd
import re


def validation_parameters():
    """
    After running the ./validation_filtering.sh script, and having classified the
    words used in the validation by Chrome Beta on chrome://topics-internals,
    run this to get a list of correct/incorrect output
    """
    output_folder = "output_web/validation/"
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


def utility_experiments():
    # E
    # manual verification
    # extract top 385
    df_crux_chrome = pd.read_csv(config.crux_chrome_csv, sep="\t")
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
    df_o = analysis_library.override_create_df()
    df_cloudflare = pd.read_csv(config.cloudflare_csv, sep="\t")
    df_cloudflare["domain"] = df_cloudflare["domain"].apply(
        lambda x: re.sub(r"[^a-zA-Z0-9]+", " ", x)
    )
    df_c = pd.merge(df_o, df_cloudflare, on="domain", how="inner")
    analysis_library.compare_topics_to_cloudflare(df_o, df_c, "override")
    analysis_library.describe_results_cloudflare_comparison("override")

    # Compare crux
    df_crux_chrome = pd.read_csv(config.crux_chrome_csv, sep="\t")
    df_cloudflare = pd.read_csv(config.cloudflare_csv, sep="\t")
    analysis_library.compare_topics_to_cloudflare(
        df_crux_chrome, df_cloudflare, "1M", True
    )
    for r in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
        analysis_library.describe_results_cloudflare_comparison("1M", r)

    # E
    df_wordnet = analysis_library.read_classified_csv(config.wordnet_csv)
    # extract top word for each topic ordered by topic id : first word = unknown topic
    top = 1
    df_extract = (
        df_wordnet.sort_values("score", ascending=False).groupby("topic_id").head(top)
    )
    df_extract.drop("score", axis=1, inplace=True)
    df_temp = df_extract.sort_values("topic_id")
    df_temp.drop("topic_id", axis=1, inplace=True)
    df_temp.to_csv(
        "output_web/subdomains/taxonomy.words",
        sep="\t",
        index=False,
        header=False,
    )

    # Now go run `./subdomains_crafting.sh`

    # After run is over, use following commands:
    analysis_library.words_crafted_subdomains(
        config.crux_chrome_csv,
        config.words_subdomains_chrome_csv,
        config.words_targeted_csv,
    )
    analysis_library.plot_crafted_subdomains("output_web/subdomains/words_results.csv")


def archive_main():
    """
    Archive of the commands to put in main to replicate results in paper
    """
    # Validation Chrome Filtering Parameters - manually inspect incorrect array
    # after, ideally len(incorrect) == 0 but floating point issues
    correct, incorrect = validation_parameters()

    # Utility
    utility_experiments()


def main():
    """
    Main function for analysis and figs
    """
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

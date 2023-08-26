import analysis
import config

import pandas as pd
import re
import sys


def subdomains_create_files(
    crux_path, top_rank, path_topics_domains, path_adv_domains, path_adv_targeted
):
    # load crux
    crux = pd.read_csv(crux_path, sep=",")
    # keep only top
    crux = crux[crux["rank"] <= max(1000, top_rank)].head(top_rank)
    # remove http(s)://
    crux["origin"] = crux.origin.apply(lambda x: re.sub("https?:\/\/", "", x))

    with open(path_topics_domains, "r") as f:
        topics = [line.rstrip("\n") for line in f]

    with open(path_adv_domains, "w") as domains, open(
        path_adv_targeted, "w"
    ) as adv_targeted:
        for row in crux.itertuples():
            for i in range(len(topics)):
                domain = topics[i] + "." + row.origin
                domains.write(domain + "\n")
                adv_targeted.write(
                    "{}\t{}\n".format(domain, i)
                )  # crafted domain with targeted id


def extract_top_word(wordnet_path, output_path):
    df_wordnet = analysis.read_classified_csv(wordnet_path)
    # extract top word for each topic ordered by topic id : first word = unknown topic
    top = 1
    df_extract = (
        df_wordnet.sort_values("score", ascending=False).groupby("topic_id").head(top)
    )
    df_extract.drop("score", axis=1, inplace=True)
    df_temp = df_extract.sort_values("topic_id")
    df_temp.drop("topic_id", axis=1, inplace=True)
    df_temp.to_csv(
        output_path,
        sep="\t",
        index=False,
        header=False,
    )


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        # check correct number of arguments has been passed
        if len(sys.argv) != 4:
            raise ValueError(
                "Wrong number of arguments passed to script, must be: extract, wordnet_path, path_topics.domains,"
            )
        else:
            wordnet_path = sys.argv[2]
            output_path = sys.argv[3]
            extract_top_word(wordnet_path, output_path)

    elif sys.argv[1] == "create":
        # check correct number of arguments has been passed
        if len(sys.argv) != 7:
            raise ValueError(
                "Wrong number of arguments passed to script, must be: create crux_path.csv, top rank, path_topics.domains, path_adv.domains, path_adv_targeted.csv"
            )
        else:
            crux_path = sys.argv[2]
            top_rank = int(sys.argv[3])
            path_topics_domains = sys.argv[4]
            path_adv_domains = sys.argv[5]
            path_adv_targeted = sys.argv[6]

            subdomains_create_files(
                crux_path,
                top_rank,
                path_topics_domains,
                path_adv_domains,
                path_adv_targeted,
            )
    elif sys.argv[1] == "results":
        crux_classified_path = sys.argv[2]
        words_subdomains_path = sys.argv[3]
        words_targeted_path = sys.argv[4]
        output_results_path = sys.argv[5]
        output_folder = sys.argv[6]
        crux_path = sys.argv[7]
        top_rank = int(sys.argv[8])

        analysis.words_crafted_subdomains(
            crux_classified_path,
            words_subdomains_path,
            words_targeted_path,
            output_results_path,
            crux_path,
            top_rank,
        )
        analysis.plot_crafted_subdomains(output_results_path, output_folder)

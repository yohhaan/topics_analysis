import analysis_library

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


def extract_top_word(output_path):
    wordnet_csv = "output/wordnet/wordnet.csv"
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
        output_path,
        sep="\t",
        index=False,
        header=False,
    )


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        # check correct number of arguments has been passed
        if len(sys.argv) != 3:
            raise ValueError(
                "Wrong number of arguments passed to script, must be: extract, path_topics.domains,"
            )
        else:
            output_path = sys.argv[2]
            extract_top_word(output_path)

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
        chrome = "_chrome"
        csv = ".csv"
        crux = "output/crux/crux"
        words_subdomains = "output/subdomains/words_subdomains"
        crux_chrome_csv = crux + chrome + csv
        words_subdomains_chrome_csv = words_subdomains + csv
        words_targeted_csv = words_subdomains + "_targeted" + csv
        analysis_library.words_crafted_subdomains(
            crux_chrome_csv, words_subdomains_chrome_csv, words_targeted_csv
        )
        analysis_library.plot_crafted_subdomains("output/subdomains/words_results.csv")

import pandas as pd
import numpy as np


def generate_parallel_input(total_nb_users, file_path, at_once=10000):
    """Generate the input text file for the parallel generation of browsing
    histories then turned into topics of interests
    Data from https://www.usenix.org/conference/soups2020/presentation/bird
    Replication: Why We Still Can't Browse in Peace: On the Uniqueness and
    Reidentifiability of Web Browsing Histories
    """
    nb_domains = [
        [1, 25],
        [26, 50],
        [51, 75],
        [76, 100],
        [101, 125],
        [126, 150],
        [151, 1116],
    ]
    mozilla_nb_users = np.array([21519, 11195, 6750, 4499, 2791, 1766, 3457])
    mozilla_proportion = mozilla_nb_users / sum(mozilla_nb_users)

    nb_users = mozilla_proportion * total_nb_users
    with open(file_path, "w") as f:
        for i in range(len(nb_users)):
            [min_range, max_range] = nb_domains[i]
            quotient = int(nb_users[i]) // at_once
            remainder = int(nb_users[i]) % at_once
            for j in range(quotient):
                f.write(
                    str(at_once) + " " + str(min_range) + " " + str(max_range) + "\n"
                )
            if remainder > 0:
                f.write(
                    str(remainder) + " " + str(min_range) + " " + str(max_range) + "\n"
                )


def output_noisy_topics_traffic(crux_path, min_nb_domains_in_top_1m):
    """Output list of topics considered noisy, i.e., if they are seen on <=
    min_nb_domains specified"""
    crux_chrome = pd.read_csv(crux_path, sep="\t")
    crux_chrome.drop(
        crux_chrome[crux_chrome["topic_id"] == -2].index, inplace=True
    )  # remove -2 - unknonw topic
    df_topics = (
        crux_chrome.groupby("topic_id")["domain"].nunique().to_frame().reset_index()
    )
    df = df_topics[df_topics["domain"] > min_nb_domains_in_top_1m]
    genuine_topics = set(list(df["topic_id"].values))
    all_topics = set(list(np.arange(1, 350)))
    noisy_topics = all_topics.difference(genuine_topics)
    return np.array(list(noisy_topics))

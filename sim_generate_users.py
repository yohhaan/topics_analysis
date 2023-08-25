import pandas as pd
import numpy as np
import sys
import random as rd


def print_output_topics(nb_unique_domains, nb_user_topics, topics):
    sorted = np.sort(topics[0:5])
    t1 = sorted[0]
    t2 = sorted[1]
    t3 = sorted[2]
    t4 = sorted[3]
    t5 = sorted[4]
    print(
        "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            nb_unique_domains, nb_user_topics, t1, t2, t3, t4, t5
        ),
        end="",
    )


if __name__ == "__main__":
    # check correct number of arguments has been passed
    if len(sys.argv) != 4:
        print(sys.argv)
        raise ValueError(
            "Wrong number of arguments passed to script, must be: nb_users range_min_nb_unique_domain, range_max_nb_unique_domain"
        )
    else:
        # load crux
        crux_order_traffic = pd.read_csv(
            "output_web/simulator/crux_order_traffic.csv", sep="\t"
        )
        crux_chrome = pd.read_csv("output_web/crux/crux_chrome.csv", sep="\t")
        crux_chrome.drop(
            crux_chrome[crux_chrome["topic_id"] == -2].index, inplace=True
        )  # remove -2

        nb_users = int(sys.argv[1])
        range_min = int(sys.argv[2])
        range_max = int(sys.argv[3])

        domains = crux_order_traffic["domain"]
        traffic_weights = crux_order_traffic["traffic"]
        traffic_weights /= traffic_weights.sum()

        nb_generated = 0
        while nb_generated < nb_users:
            # pick nb of unique domains
            nb_unique_domains = rd.randrange(range_min, range_max + 1)
            user_domains = np.random.choice(
                domains, nb_unique_domains, p=traffic_weights
            )
            df_user = crux_chrome.query("domain in @user_domains")
            topics = df_user["topic_id"].unique()

            nb_user_topics = len(topics)

            # add uniform topics from taxonomy if we are below 5 topics
            while len(topics) < 5:
                t_tax = rd.randrange(1, 349 + 1)
                if t_tax not in topics:
                    topics = np.append(topics, t_tax)

            if len(topics) == 5:
                nb_generated += 1  # do not forget to increment
                print_output_topics(nb_unique_domains, nb_user_topics, topics)
            else:
                # more than 5 topics - we randomly sample 10 combinations
                for i in range(10):
                    if nb_generated >= nb_users:
                        break
                    else:
                        t = np.random.choice(topics, 5, replace=False)
                        nb_generated += 1  # do not forget to increment
                        print_output_topics(nb_unique_domains, nb_user_topics, t)

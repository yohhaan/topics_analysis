import pandas as pd
import numpy as np
import sys
import random as rd


def generate_parallel_input(total_nb_users, file_path, at_once=2000):
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


def generate_topics_file(
    crux_order_traffic_path,
    crux_chrome_path,
    nb_users,
    range_min,
    range_max,
):
    # load crux
    crux_order_traffic = pd.read_csv(crux_order_traffic_path, sep="\t")
    crux_chrome = pd.read_csv(crux_chrome_path, sep="\t")
    crux_chrome.drop(
        crux_chrome[crux_chrome["topic_id"] == -2].index, inplace=True
    )  # remove -2

    domains = crux_order_traffic["domain"]
    traffic_weights = crux_order_traffic["traffic"]
    traffic_weights /= traffic_weights.sum()

    nb_generated = 0
    while nb_generated < nb_users:
        # pick nb of unique domains
        nb_unique_domains = rd.randrange(range_min, range_max + 1)
        user_domains = np.random.choice(domains, nb_unique_domains, p=traffic_weights)
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


def print_output_domains(user_domains):
    for domain in user_domains:
        print("{}\n".format(domain), end="")


def generate_domains_file(
    crux_order_traffic_path,
    crux_chrome_path,
    nb_users,
    range_min,
    range_max,
):
    # load crux
    crux_order_traffic = pd.read_csv(crux_order_traffic_path, sep="\t")
    crux_chrome = pd.read_csv(crux_chrome_path, sep="\t")
    crux_chrome.drop(
        crux_chrome[crux_chrome["topic_id"] == -2].index, inplace=True
    )  # remove -2

    domains = crux_order_traffic["domain"]
    traffic_weights = crux_order_traffic["traffic"]
    traffic_weights /= traffic_weights.sum()

    nb_generated = 0
    while nb_generated < nb_users:
        # pick nb of unique domains
        nb_unique_domains = rd.randrange(range_min, range_max + 1)
        user_domains = np.random.choice(domains, nb_unique_domains, p=traffic_weights)
        df_user = crux_chrome.query("domain in @user_domains")
        topics = df_user["topic_id"].unique()

        # add uniform topics from taxonomy if we are below 5 topics
        while len(topics) < 5:
            t_tax = rd.randrange(1, 349 + 1)
            if t_tax not in topics:
                topics = np.append(topics, t_tax)

        if len(topics) == 5:
            nb_generated += 1  # do not forget to increment
            print_output_domains(user_domains)
        else:
            # more than 5 topics - we randomly sample 10 combinations but
            # domains stay the same
            nb_generated += 10  # do not forget to increment
            print_output_domains(user_domains)


if __name__ == "__main__":
    if sys.argv[1] == "generate_parallel_input":
        if len(sys.argv) != 4:
            raise ValueError("Incorrect number of arguments")
        else:
            nb_users = int(sys.argv[2])
            input_path = sys.argv[3]
            generate_parallel_input(nb_users, input_path)

    elif sys.argv[1] == "topics" or sys.argv[1] == "domains":
        if len(sys.argv) != 7:
            raise ValueError("Wrong number of arguments passed to script")
        else:
            mode = sys.argv[1]
            crux_order_traffic_path = sys.argv[2]
            crux_chrome_path = sys.argv[3]
            nb_users = int(sys.argv[4])
            range_min = int(sys.argv[5])
            range_max = int(sys.argv[6])

            if mode == "topics":
                generate_topics_file(
                    crux_order_traffic_path,
                    crux_chrome_path,
                    nb_users,
                    range_min,
                    range_max,
                )
            else:
                generate_domains_file(
                    crux_order_traffic_path,
                    crux_chrome_path,
                    nb_users,
                    range_min,
                    range_max,
                )
    else:
        raise ValueError("Wrong argument passed to script")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random as rd

sns.set_theme(style="darkgrid")


def return_traffic_distribution():
    """Extracted from Figure 1 of paper World Wide View of Browsing the World
    Wide Web - page loads from Windows (desktop)"""

    scale = 1 / 44.65
    from_fig1 = {
        1: 7.59 * scale,
        2: 9.38 * scale,
        3: 10.27 * scale,
        4: 10.72 * scale,
        5: 11.07 * scale,
        6: 11.16 * scale,
        7: 11.61 * scale,
        8: 12.06 * scale,
        9: 12.35 * scale,
        10: 12.50 * scale,
        20: 14.01 * scale,
        30: 14.93 * scale,
        40: 15.42 * scale,
        50: 15.94 * scale,
        60: 16.24 * scale,
        70: 16.57 * scale,
        80: 16.93 * scale,
        90: 17.17 * scale,
        100: 17.49 * scale,
        200: 19.31 * scale,
        300: 20.30 * scale,
        400: 21.06 * scale,
        500: 21.60 * scale,
        600: 22.10 * scale,
        700: 22.59 * scale,
        800: 23.22 * scale,
        900: 23.39 * scale,
        1000: 23.76 * scale,
        2000: 26.06 * scale,
        3000: 27.42 * scale,
        4000: 28.41 * scale,
        5000: 29.25 * scale,
        6000: 29.95 * scale,
        7000: 30.43 * scale,
        8000: 30.86 * scale,
        9000: 31.30 * scale,
        10000: 31.73 * scale,
        20000: 34.14 * scale,
        30000: 35.46 * scale,
        40000: 36.49 * scale,
        50000: 37.04 * scale,
        60000: 37.50 * scale,
        70000: 37.92 * scale,
        80000: 38.27 * scale,
        90000: 38.61 * scale,
        100000: 38.89 * scale,
        200000: 40.39 * scale,
        300000: 41.22 * scale,
        400000: 41.62 * scale,
        500000: 42.00 * scale,
        600000: 42.18 * scale,
        700000: 42.48 * scale,
        800000: 42.58 * scale,
        900000: 42.77 * scale,
        1000000: 42.85 * scale,
    }
    return from_fig1


def transform_to_dictxy(d):
    """Pivot dictionary"""
    return {"x": np.array(list(d.keys())), "y": np.array(list(d.values()))}


def interpolate(dict_xy, plot_graph=False, filename="traffic"):
    """Interpolate distribution from paper"""
    from scipy.interpolate import CubicSpline

    x = np.array(dict_xy["x"])
    y = np.array(dict_xy["y"])
    spl = CubicSpline(x, y)

    if plot_graph:
        plt.clf()
        plt.plot(x, y, label="data")

        x_fitted = np.logspace(0, 6, 150)
        plt.plot(x_fitted, spl(x_fitted), label="cubicspline")

        plt.xscale("symlog")
        plt.xlim(left=0)
        plt.tight_layout()
        plt.legend()
        plt.savefig("figs/simulator/interpolation_" + filename + ".pdf")
    return spl


def crux_order_add_traffic():
    """Add distribution traffic information that was interpolated to crux
    dataset"""
    crux_order_filepath = "output/simulator/crux_total_order.csv"
    crux_order = pd.read_csv(crux_order_filepath, sep="\t")
    crux_order.drop("Unnamed: 0", axis=1, inplace=True)
    crux_order.drop("rank", axis=1, inplace=True)
    crux_order.drop("trancorank", axis=1, inplace=True)
    crux_order.drop("cloudflarerank", axis=1, inplace=True)
    crux_order.reset_index(inplace=True)  # index column is the rank
    crux_order["index"] = crux_order["index"] + 1

    d_traffic = return_traffic_distribution()
    spl_traffic = interpolate(transform_to_dictxy(d_traffic), True, "traffic")

    max_index = crux_order["index"].max()  # 991656
    index = np.arange(1, max_index + 1, 1)
    proportion = spl_traffic(index)
    proportion[1:] = proportion[1:] - spl_traffic(index[1:] - 1)
    proportion[proportion < 0] = 0  # remove potential negative values

    crux_order["traffic"] = proportion
    crux_order.to_csv("output/simulator/crux_order_traffic.csv", index=None, sep="\t")


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


def merge_crux_chrome_traffic():
    """Pre-processing: Add traffic info to crux dataset"""
    crux_order_traffic = pd.read_csv(
        "output/simulator/crux_order_traffic.csv", sep="\t"
    )
    crux_chrome = pd.read_csv("output/crux/crux_chrome.csv", sep="\t")
    crux_chrome.drop(
        crux_chrome[crux_chrome["topic_id"] == -2].index, inplace=True
    )  # remove -2
    crux_order_traffic.drop("index", axis=1, inplace=True)
    crux_chrome_traffic = crux_chrome.merge(crux_order_traffic, on="domain", how="left")
    crux_chrome_traffic.to_csv(
        "output/simulator/crux_chrome_traffic.csv", sep="\t", index=False
    )


def output_noisy_topics_traffic(min_nb_domains_in_top_1m):
    """Output list of topics considered noisy, i.e., if they are seen on <=
    min_nb_domains specified"""
    crux_chrome_traffic = pd.read_csv(
        "output/simulator/crux_chrome_traffic.csv", sep="\t"
    )
    df_topics = (
        crux_chrome_traffic.groupby("topic_id")["domain"]
        .nunique()
        .to_frame()
        .reset_index()
    )
    df = df_topics[df_topics["domain"] > min_nb_domains_in_top_1m]
    genuine_topics = set(list(df["topic_id"].values))
    all_topics = set(list(np.arange(1, 350)))
    noisy_topics = all_topics.difference(genuine_topics)
    return np.array(list(noisy_topics))

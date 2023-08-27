import sim_utils

import numpy as np
import os
import pandas as pd
import re
import sys


def get_crux_ranks(crux_path, edit_top6=False):
    # Get ranks
    ranks = pd.read_csv(crux_path, sep=",")
    ranks["origin"] = ranks.origin.apply(
        lambda x: re.sub("https?:\/\/", "", x)
    )  # Regex to remove http(s)://
    ranks.rename(columns={"origin": "domain"}, inplace=True)
    ranks.drop_duplicates(subset="domain", keep="first", inplace=True)

    if edit_top6:
        # Assign manually top ranks
        top6 = [
            "www.google.com",
            "www.youtube.com",
            "www.facebook.com",
            "www.whatsapp.com",
            "www.roblox.com",
            "www.amazon.com",
        ]
        for i in range(len(top6)):
            ranks.loc[ranks["domain"].map(lambda x: x == top6[i]), "rank"] = 1 + i

    return ranks


def total_order_crux(
    clouflare_path, crux_path, tranco_path, output_offset_folder, offset1, offset2
):
    ranks = get_crux_ranks(crux_path, True)  # edit Top6 already by passing True
    ranks = ranks[offset1:offset2]

    cloudflare_top100 = pd.read_csv(clouflare_path, sep=",")
    cloudflare_top100.drop(" Top categories", axis=1, inplace=True)
    cloudflare_top100.rename(
        columns={" Top rank": "cloudflarerank", " Top domain": "etld1"}, inplace=True
    )

    tranco = pd.read_csv(tranco_path, sep=",", header=None)
    tranco.rename(columns={0: "trancorank", 1: "etld1"}, inplace=True)

    tranco_cloudflare = tranco.merge(cloudflare_top100, on="etld1", how="outer")
    tranco_cloudflare["size_tld"] = tranco_cloudflare["etld1"].apply(
        lambda x: len(x.split("."))
    )

    ranks["size_tld"] = ranks["domain"].apply(lambda x: len(x.split(".")))
    ranks["trancorank"] = float("nan")
    ranks["cloudflarerank"] = float("nan")

    size_tlds = np.sort(tranco_cloudflare["size_tld"].unique())[::-1]

    tranco_index = 0
    for s in size_tlds:
        tranco_temp = tranco_cloudflare[tranco_cloudflare["size_tld"] == s]
        rank_temp = ranks[
            ranks["size_tld"]
            >= s
            & ~(
                (ranks["trancorank"] != float("nan"))
                | (ranks["cloudflarerank"] != float("nan"))
            )
        ]
        j = 0
        for t_row in tranco_temp.itertuples():
            j += 1
            if j == 1000:
                # reset rank_temp  to reduce search space
                j = 0
                rank_temp = ranks[
                    ranks["size_tld"]
                    >= s
                    & ~(
                        (ranks["trancorank"] != float("nan"))
                        | (ranks["cloudflarerank"] != float("nan"))
                    )
                ]

            tranco_index += 1

            indices = rank_temp[
                (
                    (rank_temp["domain"].str.endswith("." + t_row.etld1))
                    | (rank_temp["domain"] == t_row.etld1)
                )
            ].index.values
            for i in indices:
                if t_row.trancorank != float("nan"):
                    ranks.at[i, "trancorank"] = t_row.trancorank
                if t_row.cloudflarerank != float("nan"):
                    ranks.at[i, "cloudflarerank"] = t_row.cloudflarerank

    # ranks should contain the different ranks now
    ranks.drop("size_tld", axis=1, inplace=True)
    ranks.sort_values(by=["rank", "cloudflarerank", "trancorank"], inplace=True)
    ranks.to_csv(
        output_offset_folder + "/crux_order_{}_{}.csv".format(offset1, offset2),
        index=False,
    )


def merge_csv(output_offset_folder, output_order_path):
    # collect all csv files under output_offset_folder
    csv_paths = [f for f in os.listdir(output_offset_folder) if f.endswith(".csv")]
    dfs = []
    for path in csv_paths:
        df = pd.read_csv(output_offset_folder + "/" + path)
        dfs.append(df)
    crux_order = pd.concat(dfs, ignore_index=True)
    crux_order.sort_values(by=["rank", "cloudflarerank", "trancorank"], inplace=True)
    crux_order.to_csv(output_order_path, sep="\t")


def crux_order_add_traffic(output_order_path, output_order_traffic_path):
    """Add distribution traffic information that was interpolated to crux
    dataset"""
    crux_order = pd.read_csv(output_order_path, sep="\t")
    crux_order.drop("Unnamed: 0", axis=1, inplace=True)
    crux_order.drop("rank", axis=1, inplace=True)
    crux_order.drop("trancorank", axis=1, inplace=True)
    crux_order.drop("cloudflarerank", axis=1, inplace=True)
    crux_order.reset_index(inplace=True)  # index column is the rank
    crux_order["index"] = crux_order["index"] + 1

    d_traffic = return_traffic_distribution()
    spl_traffic = interpolate(transform_to_dictxy(d_traffic))

    max_index = crux_order["index"].max()
    index = np.arange(1, max_index + 1, 1)
    proportion = spl_traffic(index)
    proportion[1:] = proportion[1:] - spl_traffic(index[1:] - 1)
    proportion[proportion < 0] = 0  # remove potential negative values

    crux_order["traffic"] = proportion
    crux_order.to_csv(output_order_traffic_path, index=None, sep="\t")


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


def interpolate(dict_xy):
    """Interpolate distribution from paper World wide view of browsing the world
    wide web https://dl.acm.org/doi/10.1145/3517745.3561418"""
    from scipy.interpolate import CubicSpline

    x = np.array(dict_xy["x"])
    y = np.array(dict_xy["y"])
    spl = CubicSpline(x, y)
    return spl


if __name__ == "__main__":
    if sys.argv[1] == "order":
        if len(sys.argv) != 9:
            raise ValueError("Wrong number of arguments")
        else:
            clouflare_path = sys.argv[2]
            crux_path = sys.argv[3]
            tranco_path = sys.argv[4]
            output_offset_folder = sys.argv[5]
            nb_domains = int(sys.argv[6])
            nb_cpus = int(sys.argv[7])
            offset = int(sys.argv[8])

            n = round(nb_domains / nb_cpus)
            offset1 = offset * n
            offset2 = (offset + 1) * n

            total_order_crux(
                clouflare_path,
                crux_path,
                tranco_path,
                output_offset_folder,
                offset1,
                offset2,
            )
    elif sys.argv[1] == "merge":
        if len(sys.argv) != 5:
            raise ValueError("Wrong number of arguments")
        else:
            output_offset_folder = sys.argv[2]
            output_order_path = sys.argv[3]
            output_order_traffic_path = sys.argv[4]
            merge_csv(output_offset_folder, output_order_path)
            crux_order_add_traffic(output_order_path, output_order_traffic_path)

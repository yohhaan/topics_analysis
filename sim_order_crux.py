import utils
import sim_utils

import sys
import pandas as pd
import numpy as np


def total_order_crux(offset1, offset2):
    clouflare_path = "sandbox_dependencies/topics/cloudflare-radar-domains-top100.csv"
    tranco_filepath = "sandbox_dependencies/topics/top-1m.csv"
    ranks = utils.get_crux_ranks(True)  # edit Top6 already by passing True
    ranks = ranks[offset1:offset2]

    cloudflare_top100 = pd.read_csv(clouflare_path, sep=",")
    cloudflare_top100.drop(" Top categories", axis=1, inplace=True)
    cloudflare_top100.rename(
        columns={" Top rank": "cloudflarerank", " Top domain": "etld1"}, inplace=True
    )

    tranco = pd.read_csv(tranco_filepath, sep=",", header=None)
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

            print(offset1, tranco_index)
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
        "output/simulator/crux_order/crux_total_order_{}_{}.csv".format(
            offset1, offset2
        ),
        index=False,
    )


def merge_csv(n):
    output_path = "output/simulator/crux_order/crux_total_order_{}_{}.csv"
    crux_order = pd.read_csv(output_path.format(0, n))
    for i in range(15):
        crux_temp = pd.read_csv(output_path.format(n * (i + 1), n * (i + 2)))
        crux_order = pd.concat([crux_order, crux_temp])
    crux_order.sort_values(by=["rank", "cloudflarerank", "trancorank"], inplace=True)
    crux_order.to_csv("output/simulator/crux_total_order.csv", sep="\t")


if __name__ == "__main__":
    # N = 991656 # unique domains in CrUX
    n = 61979  # round(N / nb_cpus) in our case nb_cpus=16
    if sys.argv[1] == "generate":
        offset = int(sys.argv[2])
        total_order_crux(offset * n, (offset + 1) * n)
    elif sys.argv[1] == "merge":
        merge_csv(n)
        sim_utils.crux_order_add_traffic()

import pandas as pd
import re
import sys

if __name__ == "__main__":
    # check correct number of arguments has been passed
    if len(sys.argv) != 6:
        raise ValueError(
            "Wrong number of arguments passed to script, must be: crux_path.csv, top rank, topics.domains, adv.domains, adv_targeted.csv"
        )
    else:
        # load crux
        crux = pd.read_csv(sys.argv[1], sep=",")
        # keep only top
        crux = crux[crux["rank"] <= int(sys.argv[2])]
        # remove http(s)://
        crux["origin"] = crux.origin.apply(lambda x: re.sub("https?:\/\/", "", x))

        with open(sys.argv[3], "r") as f:
            topics = [line.rstrip("\n") for line in f]

        with open(sys.argv[4], "w") as domains, open(sys.argv[5], "w") as adv_targeted:
            for row in crux.itertuples():
                for i in range(len(topics)):
                    domain = topics[i] + "." + row.origin
                    domains.write(domain + "\n")
                    adv_targeted.write(
                        "{}\t{}\n".format(domain, i)
                    )  # crafted domain with targeted id

import os
import pandas as pd
import sys
import re


def validation_parameters(validation_chrome_path, validation_beta_path):
    """
    After running the ./validation_filtering.sh script, and having classified the
    words used in the validation by Chrome Beta on chrome://topics-internals,
    run this to get a list of correct/incorrect output
    """
    correct = []
    incorrect = []
    df_validation_chrome = pd.read_csv(validation_chrome_path, sep="\t")

    with open(validation_beta_path, "r") as f:
        beta = f.readlines()

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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect number of arguments passed to script, need to be paths to both classification that need comparison"
        )
    else:
        validation_chrome_path = sys.argv[1]
        validation_beta_path = sys.argv[2]

        if not (os.path.isfile(validation_chrome_path)) or not (
            os.path.isfile(validation_beta_path)
        ):
            raise Exception("Error: file(s) missing, check validation_filtering.md")
        else:
            correct, incorrect = validation_parameters(
                validation_chrome_path, validation_beta_path
            )

            print("Size of incorrect set: {}".format(len(incorrect)))
            print("Incorrect set: {}".format(incorrect))

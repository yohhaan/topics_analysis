import config
import dependencies

from matplotlib.colors import SymLogNorm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import re
import seaborn as sns
import os


sns.set_theme(style="darkgrid")


def savefig(path, size=[4, 3]):
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.gcf().set_size_inches(*size)
    plt.tight_layout(
        pad=0,
    )
    plt.savefig(path, bbox_inches="tight")
    plt.clf()


def override_create_df():
    """
    Create Pandas Dataframe of override list
    """
    domains = []
    topics = []
    scores = []
    for entry in config.web_override_list.entries:
        # extract topic ids manually classified
        ids = entry.topics.topic_ids
        if ids == []:
            # empty
            domains.append(entry.domain)
            topics.append(-2)  # -2 means unknown/no topic id, likely sensitive
            scores.append(1)  # manually annotated
        else:
            for id in ids:
                domains.append(entry.domain)
                topics.append(id)
                scores.append(1)  # manually annotated, we assume score equal to 1
    df_override = pd.DataFrame({"domain": domains, "topic_id": topics, "score": scores})
    return df_override


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


def read_chrome_csv(filename):
    """
    Read csv classified by model with chrome filtering strategy already applied
    """
    df = pd.read_csv(
        filename,
        sep="\t",
        dtype={"domain": str, "topic_id": int, "score": float},
    )

    return df


def histplot_topics_per_domain(df, output_folder):
    """
    Hisplot of domains count binned by number of topics individually assigned to
    domain
    Unknonw topic is considered as no topic assigned to that domain
    """
    plt.clf()
    # replace unknown topic by None
    df["topic_id"] = df["topic_id"].replace(-2, None)
    data = df.groupby(["domain"])["topic_id"].nunique()
    # countplot
    plot = sns.countplot(x=data)
    # replace back
    df["topic_id"] = df["topic_id"].replace(float("nan"), -2)
    # display count value on top
    plot.bar_label(plot.containers[0])
    plot.set(xlabel="Number of topic(s) per individual domain", ylabel="Domains count")
    plt.tight_layout()
    savefig(output_folder + "/histplot_topics_per_domain.pdf")
    return data


def cdf_histplot_domains_per_topic(df, output_folder):
    """
    Histplot of topics count binned per number of domain(s) for each topic
    Ignore Unknown topic
    """
    # add topics potentially non observed / note: -2 is discarded
    merged = df.merge(
        pd.DataFrame({"topic_id": np.arange(1, 350)}), how="right", on="topic_id"
    )
    # get number of domains for each topic
    data = merged.groupby("topic_id")["domain"].nunique().reset_index()
    plt.clf()
    # cdf
    sns.ecdfplot(data=data, x="domain", stat="count")
    plt.legend(["eCDF"])
    # generate bins and bins labels
    max_domains = data.domain.max()
    if max_domains > 2048:
        max_exponent = int(np.log10(max_domains))
        base = 10
        # No label for the one before the max value (they overlap most of the times)
        bins_labels = np.concatenate(
            [[0], base ** (np.arange(0, max_exponent)), [""], [max_domains]]
        )
    else:
        max_exponent = int(np.log2(max_domains))
        base = 2
        # No label for the one before the max value (they overlap most of the times)
        bins_labels = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, max_domains]
        plt.xticks(rotation=45)
    bins = np.concatenate(
        [[0], base ** (np.arange(0, max_exponent + 1)), [max_domains]]
    )

    # histplot
    plot = sns.histplot(data=data, x="domain", bins=bins)
    # axis
    plot.set(xlabel="Number of domain(s) per topic", ylabel="Topics count")
    plot.set_xscale("symlog")
    plot.set_xlim(left=0)
    plot.set_ylim([0, 350])
    plot.set_xticks(bins, bins_labels)
    plt.tight_layout()
    savefig(output_folder + "/cdf_histplot_domains_per_topic.pdf")
    return data


def graph_describe_all(df, output_folder):
    data1 = histplot_topics_per_domain(df, output_folder)
    data2 = cdf_histplot_domains_per_topic(df, output_folder)
    with open(output_folder + "/stats.txt", "w") as f:
        f.write("Stats about topics per domain:\n {} \n".format(data1.describe()))
        f.write("Stats about domains per topic:\n {} \n".format(data2.describe()))


def compare_to_ground_truth(
    df_truth, df_predicted, output_folder, filename, keep_same_nb=True
):
    """
    Compare ground truth (manually annotated 10k) to prediction, keeping same
    top number of topics if keep_same_nb is set to True, otherwise we assume
    that prediction has already been filtered out and we treat it directly.
    0 is considered as the unknown topic.
    """

    # replace unknown topic by 0
    df_truth["topic_id"] = df_truth["topic_id"].replace(-2, 0)
    df_predicted["topic_id"] = df_predicted["topic_id"].replace(-2, 0)
    # extract number of topics per domain in manual list
    df_truth.sort_values(by=["domain"], inplace=True)
    df_count = df_truth.groupby(["domain"])["topic_id"].nunique().reset_index()

    dice = np.zeros(len(df_count))
    jaccard = np.zeros(len(df_count))
    overlap = np.zeros(len(df_count))
    cm = np.zeros([350, 350])
    i = 0

    for row in df_count.itertuples():
        domain_truth = df_truth[df_truth.domain == row.domain]
        # keep same number of top topics as in df_o or no
        if keep_same_nb:
            domain_prediction = (
                df_predicted[df_predicted.domain == row.domain]
                .sort_values(by=["score"], ascending=[False])
                .head(row.topic_id)
            )
        else:
            domain_prediction = df_predicted[df_predicted.domain == row.domain]
        truth = domain_truth["topic_id"]
        pred = domain_prediction["topic_id"]
        intersection = list(set(truth).intersection(pred))
        # len(truth) > 0
        dice[i] = 2 * len(intersection) / (len(truth) + len(pred))
        jaccard[i] = len(intersection) / (len(truth) + len(pred) - len(intersection))
        if len(pred) != 0:
            overlap[i] = len(intersection) / min(len(truth), len(pred))

        for id in intersection:
            cm[id][id] += 1

        diff_truth = list(set(truth).symmetric_difference(intersection))
        diff_pred = list(set(pred).symmetric_difference(intersection))

        for idt in diff_truth:
            for idp in diff_pred:
                cm[idt][idp] += 1 / len(diff_pred)
        i += 1

    # replace back unknown topic by -2
    df_truth["topic_id"] = df_truth["topic_id"].replace(0, -2)
    df_predicted["topic_id"] = df_predicted["topic_id"].replace(0, -2)
    # save for future analysis or reuse
    np.save(output_folder + "/" + filename + "_confusion_matrix.npy", cm)
    np.save(output_folder + "/" + filename + "_dice.npy", dice)
    np.save(output_folder + "/" + filename + "_jaccard.npy", jaccard)
    np.save(output_folder + "/" + filename + "_overlap.npy", overlap)


def results_model_ground_truth(df_o, output_folder, filename):
    cm = np.load(output_folder + "/" + filename + "_confusion_matrix.npy")
    dice = np.load(output_folder + "/" + filename + "_dice.npy").flatten()
    jaccard = np.load(output_folder + "/" + filename + "_jaccard.npy").flatten()
    overlap = np.load(output_folder + "/" + filename + "_overlap.npy").flatten()

    n = 350
    N_domains = len(df_o)
    accuracy = np.trace(cm) / N_domains
    # Add missing topic_ids
    df_o["topic_id"] = df_o["topic_id"].replace(-2, 0)
    merged = df_o.merge(
        pd.DataFrame({"topic_id": np.arange(0, 350)}), how="right", on="topic_id"
    )
    df_o["topic_id"] = df_o["topic_id"].replace(0, -2)
    # get number of domains for each topic
    weights = merged.groupby("topic_id")["domain"].nunique().to_numpy()
    topics_accuracy = np.zeros(n)
    # weighted and balance accuracy
    for i in range(n):
        if np.sum(cm[i]) != 0:
            topics_accuracy[i] = cm[i][i] / np.rint(np.sum(cm[i]))
    balanced_accuracy = np.sum(topics_accuracy) / n
    weighted_balanced_accuracy = np.dot(weights, topics_accuracy) / (n * sum(weights))

    with open(output_folder + "/" + filename + "_comparison_stats.txt", "w") as f:
        f.write("----STATS {}----\n".format(filename))
        f.write("Accuracy is: {}\n".format(accuracy))
        f.write("Balanced Accuracy is: {}\n".format(balanced_accuracy))
        f.write(
            "Weighted Balanced Accuracy is: {}\n".format(weighted_balanced_accuracy)
        )
        f.write("----\n")
        f.write(
            "Proportion all_correct: {}\n".format(np.sum(jaccard >= 1) / len(jaccard))
        )
        f.write("Proportion some_correct (dice): {}\n".format(np.sum(dice) / len(dice)))
        f.write(
            "Proportion some_correct (jaccard): {}\n".format(
                np.sum(jaccard) / len(jaccard)
            )
        )
        f.write(
            "Proportion some_correct (overlap): {}\n".format(
                np.sum(overlap) / len(overlap)
            )
        )
        f.write(
            "Proportion one_correct: {}\n".format(np.sum(jaccard > 0) / len(jaccard))
        )
        f.write("--------\n")


def taxonomy(output_folder="output_web"):
    """
    Output stats about the initial taxonomy
    """
    taxonomy = config.web_taxonomy.copy()
    taxonomy.pop(-2)  # pop unknown topic to recover initial taxonomy from Google

    subcategories = {}  # will be dict where keys are broader categories ids
    for id in taxonomy.keys():  # works because alphabetically ordered in taxonomy
        is_sub = False
        for cat in subcategories.keys():
            if taxonomy[cat] in taxonomy[id]:
                subcategories[cat].append(id)
                is_sub = True
                break
        if not (is_sub):
            subcategories[id] = [id]

    parent = [re.sub("&", "\&", taxonomy[id]) for id in subcategories.keys()]
    nb_topics = [len(v) for v in subcategories.values()]

    df = pd.DataFrame({"Parent category": parent, "Number of topics": nb_topics})
    # latex table
    with open(output_folder + "/taxonomy_table.tex", "w") as f:
        f.write(
            df.style.hide(axis="index").to_latex(
                hrules=True,
                position="!ht",
                column_format="lc",
                caption="Distribution of topics in initial taxonomy; number of topics (including parent topic) per parent category",
            )
        )
    with open(output_folder + "/taxonomy_stats.txt", "w") as f:
        f.write("----TAXONOMY----\n")
        f.write("size without unknown topic: {}\n".format(len(taxonomy)))
        f.write("Stats about parent topics:\n{}\n".format(df.describe()))


def chrome_filter(
    df,
    filename="",
):
    """
    CHROME PARAMETERS see chromium/src/chrome/browser/optimization_guide/page_content_annotations_service_browsertest.cc
    Perform Chrome's algorithm to keep top topics
    And save to disk if filename specified
    """
    # extract top max topics for each domain of higher score
    df_top_max = (
        df.sort_values("score", ascending=False)
        .groupby("domain")
        .head(config.web_max_topics)
    )
    # compute sum of top scores for each domain
    df_top_scores_sum = df_top_max.groupby("domain")["score"].sum().to_frame()
    # rename column
    df_top_scores_sum.rename({"score": "sum"}, axis=1, inplace=True)
    # drop if top score is less than the minimum desired
    df_top_max.drop(
        df_top_max[df_top_max["score"] < config.web_min_topic_score].index, inplace=True
    )
    # merge to add scores sum
    df_top_max = df_top_max.merge(df_top_scores_sum, on="domain", how="left")
    # extract too strong Unknown Topic
    df_too_strong_none = df_top_max[
        (df_top_max["topic_id"] == -2)
        & (df_top_max["score"] / df_top_max["sum"] > config.web_min_unknown_score)
    ]
    # left minus join to remove domains with too strong none topic (will add
    # back later just the none topic for them)
    df_top_max = df_top_max.merge(
        df_too_strong_none["domain"], on="domain", how="outer", indicator=True
    ).query('_merge == "left_only"')
    # drop column '_merge == "left_only"'
    df_top_max.drop("_merge", axis=1, inplace=True)
    # remove other none/unknown topics
    df_top_max.drop(df_top_max[df_top_max["topic_id"] == -2].index, inplace=True)
    # remove if score after normalization is below threshold
    df_top_max.drop(
        df_top_max[
            df_top_max["score"] / df_top_max["sum"]
            < config.web_min_normalized_score_within_top_n
        ].index,
        inplace=True,
    )
    # drop column 'sum'
    df_top_max.drop("sum", axis=1, inplace=True)
    # Some domains may have totally disappeared (too strong Unknown but also
    # others), we add them back here
    df_top_max = df_top_max.merge(
        df[df["topic_id"] == -2], on="domain", how="outer", suffixes=("", "_temp")
    )
    df_top_max["topic_id"] = df_top_max["topic_id"].fillna(df_top_max["topic_id_temp"])
    df_top_max["score"] = df_top_max["score"].fillna(df_top_max["score_temp"])
    df_top_max = df_top_max.drop(df_top_max.filter(regex="_temp").columns, axis=1)
    # reset index
    df_top_max.reset_index(drop=True, inplace=True)
    if filename != "":
        df_top_max.to_csv(filename, sep="\t", index=False)
    return df_top_max


###############################
###############################


### CrUX manual verification ###
def extract_sample_size_x(df, x, foldername, filename):
    """
    Extract uniform sample from df and save it into specified folder
    """
    sample = (
        df.sort_values(by=["score"], ascending=[False])
        .groupby("domain")
        .head(1)
        .sample(x)
    )
    sample.to_csv(
        "output_web/" + foldername + "/" + filename + "sample_size_" + str(x) + ".csv",
        sep="\t",
    )


def crux_extract_sample_size_x(df, x, foldername, filename):
    """
    Extract uniform sample of x classified domains not in override list
    """
    import utils

    df_extract_temp = (
        df.sort_values(by=["score"], ascending=[False])
        .groupby("domain")
        .head(1)
        .sample(3 * x)
    )
    df_extract_temp["in_override"] = df_extract_temp.domain.apply(
        lambda x: 1
        if utils.check_web_override_list(utils.process_domain(x)) != None
        else 0
    )
    sample = df_extract_temp[df_extract_temp["in_override"] == 0].head(x)
    sample.drop("in_override", inplace=True, axis=1)

    output_path = "output_web/" + foldername + "/" + filename + "_sample.jsonl"
    with open(output_path, "w") as f:
        f.write(sample.to_json(orient="records", lines=True, force_ascii=False))


def crux_augment_with_meta_description(foldername, filename):
    input_file = "output_web/" + foldername + "/" + filename + "_sample.jsonl"
    df = pd.read_json(input_file, orient="records", lines=True)

    df["meta_description"] = df.domain.apply(lambda x: get_meta_description(x))

    output_path = (
        "output_web/" + foldername + "/" + filename + "_augmented_sample.jsonl"
    )
    with open(output_path, "w") as f:
        f.write(df.to_json(orient="records", lines=True, force_ascii=False))


def get_meta_description(domain):
    import requests
    from bs4 import BeautifulSoup

    url = "http://" + domain
    print(domain)
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
    except:
        response = None
    if response != None:
        soup = BeautifulSoup(response.text, features="html.parser")
        if soup.findAll("meta", attrs={"name": "description"}):
            return soup.find("meta", attrs={"name": "description"}).get("content")
    return None


def crux_verification(foldername, filename):
    """
    Manual verification of classified domains
    Input: .jsonl file created by corresponding function
    Output: .jsonl file with verification score: 3 = correct, 2 = somewhat
    related, 1 = incorrect.
    """
    input_file = "output_web/" + foldername + "/" + filename + "_augmented_sample.jsonl"
    output_file = "output_web/" + foldername + "/" + filename + "_verified.jsonl"

    df = pd.read_json(input_file, orient="records", lines=True)

    for row in df.itertuples():
        os.system("clear")
        print("Domain: ", row.domain)
        print("TOPIC:", config.web_taxonomy[row.topic_id])
        print()
        print("DESCRIPTION: ", row.meta_description)
        print()
        print("Rate topic classification: 3=exact, 2=related, 1=not at all")
        rating = int(input("YOUR CHOICE: "))
        r = "null"
        if rating in [1, 2, 3]:
            r = rating
        df_row = pd.DataFrame(
            {"domain": [row.domain], "topic_id": [row.topic_id], "rating": [r]}
        )
        with open(output_file, "a") as f:
            f.write(df_row.to_json(orient="records", lines=True, force_ascii=False))


### CrUX comparison Topics classification and Cloudflare categorization ###
# after running cloudflare_categorization.sh and manually mapping Cloudflare categories
# to Topics run following functions


def parse_cloudflare_topics_mapping(
    mapping_path="cloudflare_categories_manual_mapping_topics.json",
    output_dict_path="output_web/cloudflare/mapping_categories.pickle",
):
    import json
    import pickle

    cloudflare = {}
    with open(mapping_path, "r") as f:
        mapping = json.load(f)
    for elt in mapping:
        subcategories = elt["subcategories"]
        if subcategories != None:
            sub_ids = []
            for elt_bis in subcategories:
                cloudflare[elt_bis["id"]] = elt_bis["topic_id"]
                for id in elt_bis["topic_id"]:
                    if id not in sub_ids:
                        sub_ids.append(id)
            cloudflare[elt["id"]] = sub_ids
        else:
            cloudflare[elt["id"]] = elt["topic_id"]

    # save to disk dict as .pickle
    with open(output_dict_path, "wb") as output:
        pickle.dump(cloudflare, output, protocol=pickle.HIGHEST_PROTOCOL)


def compare_topics_to_cloudflare(
    df_crux_chrome,
    df_crux_cloudflare,
    filename,
    ranks_bool=False,
    ranks_filepath="sandbox_dependencies/topics_web/crux.csv",
    dict_path="output_web/cloudflare/mapping_categories.pickle",
):
    import pickle
    import re

    with open(dict_path, "rb") as f:
        mapping = pickle.load(f)

    df_cloudflare = df_crux_cloudflare[
        df_crux_cloudflare["cloudflare_id"] != -10
    ]  # id used in python script when Cloudflare API does not return a result

    if ranks_bool:
        # Get ranks
        ranks = pd.read_csv(ranks_filepath, sep=",")
        # Regex to remove http(s)://
        ranks["origin"] = ranks.origin.apply(lambda x: re.sub("https?:\/\/", "", x))
        ranks.rename(columns={"origin": "domain"}, inplace=True)
        ranks = ranks.drop_duplicates(subset="domain", keep="first")

        df_cloudflare = df_cloudflare.merge(ranks, on=["domain"], how="left")

    df_cloudflare_unique = df_cloudflare["domain"].unique()

    intersection = {}
    overlap = {}
    if ranks_bool:
        for r in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
            intersection[r] = []
            overlap[r] = []
    else:
        rank = "no_rank"
        intersection[rank] = []
        overlap[rank] = []

    i = 0
    for domain in df_cloudflare_unique:
        print(i)
        i += 1
        cloudflare_pred = df_cloudflare[df_cloudflare.domain == domain]
        topics_pred = df_crux_chrome[df_crux_chrome.domain == domain]
        topics_tids = topics_pred["topic_id"]
        cloudflare_cids = cloudflare_pred["cloudflare_id"]
        cloudflare_tids = []
        for c in cloudflare_cids:
            topics = mapping[c]
            for t in topics:
                if t not in cloudflare_tids:
                    cloudflare_tids.append(t)

        inter = list(set(cloudflare_tids).intersection(topics_tids))

        if ranks_bool:
            rank = cloudflare_pred["rank"].values[0]

        intersection[rank].append(len(inter))
        overlap[rank].append(len(inter) / len(topics_tids))

    with open(
        "output_web/cloudflare/result_intersection_" + filename + ".pickle", "wb"
    ) as output:
        pickle.dump(intersection, output, protocol=pickle.HIGHEST_PROTOCOL)

    with open(
        "output_web/cloudflare/result_overlap_" + filename + ".pickle", "wb"
    ) as output:
        pickle.dump(overlap, output, protocol=pickle.HIGHEST_PROTOCOL)


def describe_results_cloudflare_comparison(filename, rank="no_rank"):
    import pickle

    with open(
        "output_web/cloudflare/result_intersection_" + filename + ".pickle", "rb"
    ) as f:
        intersection = pickle.load(f)
    with open(
        "output_web/cloudflare/result_overlap_" + filename + ".pickle", "rb"
    ) as f:
        overlap = pickle.load(f)

    if rank != "no_rank":
        intersection_temp = []
        overlap_temp = []
        for r in intersection.keys():
            if r <= rank:
                intersection_temp = np.concatenate(
                    (intersection_temp, intersection[r]), axis=None
                )
                overlap_temp = np.concatenate((overlap_temp, overlap[r]), axis=None)
        print("-----{}-----".format(rank))
        print("Nb domains: {}".format(len(intersection_temp)))
        print("Proportion overlap: {}".format(np.sum(overlap_temp) / len(overlap_temp)))
        print(
            "Proportion one_correct: {}".format(
                np.sum(intersection_temp > 0) / len(intersection_temp)
            )
        )
    else:
        print("Nb domains: {}".format(len(intersection["no_rank"])))
        print(
            "Proportion overlap: {}".format(
                np.sum(overlap["no_rank"]) / len(overlap["no_rank"])
            )
        )
        print(
            "Proportion one_correct: {}".format(
                np.sum(np.array(intersection["no_rank"]) > 0)
                / len(intersection["no_rank"])
            )
        )


### Crafting Subdomains ###
def words_crafted_subdomains(
    crux_chrome_csv,
    words_subdomains_chrome_csv,
    words_targeted_csv,
    output_path_results,
):
    # extract crux to get rank
    crux = pd.read_csv("sandbox_dependencies/topics_web/crux.csv", sep=",")
    # keep only top
    crux = crux[crux["rank"] <= 10000]
    # remove http(s)://
    crux["domain"] = crux.origin.apply(lambda x: re.sub("https?:\/\/", "", x))
    crux.drop("origin", axis=1, inplace=True)
    # merge with classification of crux
    df_crux_chrome = pd.read_csv(crux_chrome_csv, sep="\t")
    df_crux_chrome = df_crux_chrome.merge(
        crux, on="domain", how="inner", indicator=True
    ).query('_merge == "both"')
    df_crux_chrome.drop("_merge", axis=1, inplace=True)

    df_words_subdomains = pd.read_csv(words_subdomains_chrome_csv, sep="\t")
    df_words_subdomains.drop_duplicates(inplace=True)
    df_words_subdomains["topic_id"].replace(-2, 0, inplace=True)
    # get targets
    df_words_targeted = pd.read_csv(words_targeted_csv, sep="\t", header=None)
    df_words_targeted.columns = ["domain", "target"]
    # targeted results
    df_words = df_words_subdomains.merge(df_words_targeted, how="left", on="domain")
    df_words["targeted"] = np.where(df_words["topic_id"] == df_words["target"], 1, 0)

    # untargeted results
    df_words["origin"] = df_words.domain.apply(lambda x: x.split(".", 1)[1])
    df_words["untargeted"] = df_words.apply(
        lambda x: x["topic_id"]
        not in df_crux_chrome[df_crux_chrome["domain"] == x["origin"]]["topic_id"],
        axis=1,
    )
    df_words.to_csv(output_path_results, sep="\t")


def plot_crafted_subdomains(output_path_results, output_folder):
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="darkgrid")

    df = pd.read_csv(output_path_results, sep="\t")

    df.drop("Unnamed: 0", axis=1, inplace=True)
    df.drop_duplicates(inplace=True)

    with open(output_folder + "/targeted_untargeted_stats.txt", "w") as f:
        f.write("Targeted: {}\n".format(df["targeted"].sum() / df["domain"].nunique()))
        f.write(
            "Untargeted: {}\n".format(
                np.sum(df.groupby(["domain", "target"])["untargeted"].sum() > 0)
                / df["domain"].nunique()
            )
        )

        # extract dataframes for plotting
        df_data = pd.DataFrame(
            {"successes": df.groupby("origin")["targeted"].sum(), "type": "Targeted"}
        )
        f.write("---Stats targeted---\n{}\n".format(df_data["successes"].describe()))

        df_temp = (
            df.groupby(["origin", "domain", "target"])["untargeted"].sum().reset_index()
        )
        df_temp["untargeted_bis"] = df_temp["untargeted"] > 0
        df_untargeted = pd.DataFrame(
            {
                "successes": df_temp.groupby("origin")["untargeted_bis"].sum(),
                "type": "Untargeted",
            }
        )
        f.write(
            "---Stats untargeted---\n{}\n".format(df_untargeted["successes"].describe())
        )

    df_data = pd.concat([df_data, df_untargeted])

    plt.clf()
    # cdf
    plot = sns.ecdfplot(data=df_data, x="successes", stat="proportion", hue="type")
    plot.set(xlabel="Number of subdomains misclassified", ylabel="Proportion")
    # plot.set_xscale("symlog")
    plot.set_xlim([0, 355])
    plot.set_ylim([-0.02, 1.02])
    plot.legend_.set_title(None)
    sns.move_legend(plot, "center right")
    plt.tight_layout()
    savefig(output_folder + "/targeted_untargeted_success.pdf")

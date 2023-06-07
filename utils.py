import config


def process_domain(domain):
    """
    Replaces a set of common domain characters with white space. See
    https://source.chromium.org/chromium/chromium/src/+/main:components/optimization_guide/core/page_topics_model_executor.cc;l=211?q=meaningless%20f:optimization_guide&ss=chromium
    """
    replace_chars = ["-", "_", ".", "+"]
    for rc in replace_chars:
        domain = domain.replace(rc, " ")
    return domain


def check_override_list(domain):
    """
    Check if domain is in override_list
    """
    for entry in config.override_list.entries:
        if entry.domain == domain:
            return entry.topics.topic_ids
    return None


def ml_model_csv_header():
    """
    Print the csv header: domain\t-2\t1...
    """
    header = "domain"
    for topic in config.taxonomy.keys():
        header += "\t{}".format(topic)
    print(header)


def chrome_csv_header():
    print("domain\ttopic_id\tscore")


def get_crux_ranks(edit_top6=False):
    # Get ranks
    import pandas as pd
    import re

    crux_ranks = "sandbox_dependencies/topics/crux.csv"
    ranks = pd.read_csv(crux_ranks, sep=",")
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


def is_etld1_in_domains(etld1, domains):
    for d in domains:
        if d.endswith(etld1):
            return True
    return False

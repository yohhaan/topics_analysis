import config
import re


def process_domain(domain):
    """
    Replaces a set of common domain characters with white space. See
    https://source.chromium.org/chromium/chromium/src/+/main:components/optimization_guide/core/page_topics_model_executor.cc;l=211?q=meaningless%20f:optimization_guide&ss=chromium
    """
    replace_chars = ["-", "_", ".", "+"]
    for rc in replace_chars:
        domain = domain.replace(rc, " ")
    return domain


def check_web_override_list(domain):
    """
    Check if domain is in override_list
    """
    for entry in config.web_override_list.entries:
        if entry.domain == domain:
            return entry.topics.topic_ids
    return None


def chrome_ml_model_csv_header():
    """
    Print the csv header: domain\t-2\t1...
    """
    header = "domain"
    for topic in config.web_taxonomy.keys():
        header += "\t{}".format(topic)
    print(header)


def chrome_csv_header():
    print("domain\ttopic_id\tscore")

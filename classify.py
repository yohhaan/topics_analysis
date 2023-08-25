import config
import dependencies
import utils

import sys


def chrome_ml_model(domains):
    """
    Runs the model classifier and return only topics that pass chrome filter
    """
    for domain in domains:
        print("Domain: ", domain)
        processed_domain = utils.process_domain(domain)
        topics = config.web_model.classify(processed_domain)
        cats = sorted(
            topics.classifications[0].categories,
            key=lambda x: x.score,
            reverse=True,
        )[0 : config.web_max_topics]
        top_sum = 0
        unknown_score = None
        for c in cats:
            top_sum += c.score
            if int(c.category_name) == -2:
                unknown_score = c.score
        if unknown_score and unknown_score / top_sum > config.web_min_unknown_score:
            print("{}\t{}\t{}".format(unknown_score, -2, config.web_taxonomy[-2]))
            print("\n")
            continue
        other = False
        for c in cats:
            if (
                int(c.category_name) != -2
                and c.score >= config.web_min_topic_score
                and c.score / top_sum >= config.web_min_normalized_score_within_top_n
            ):
                other = True
                print(
                    "{}\t{}\t{}".format(
                        c.score,
                        c.category_name,
                        config.web_taxonomy[int(c.category_name)],
                    )
                )
        if not (other):
            print("{}\t{}\t{}".format(unknown_score, -2, config.web_taxonomy[-2]))
        print("\n")


def chrome_ml_model_csv(domains):
    """
    Runs the model classifier and print scores for every topic in the taxonomy
    """
    for domain in domains:
        processed_domain = utils.process_domain(domain)
        line = "{}".format(domain)
        topics = config.web_model.classify(processed_domain)
        cats = sorted(
            topics.classifications[0].categories, key=lambda x: int(x.category_name)
        )
        for c in cats:
            line += "\t{}".format(c.score)
        print(line + "\n", end="")


def chrome_csv(domains):
    """
    Chrome classifier checks override list first before calling the model
    classifier and outputting top 5 categories if domain was not present
    """
    for domain in domains:
        processed_domain = utils.process_domain(domain)
        topics = utils.check_web_override_list(processed_domain)
        if topics != None:
            if topics == []:
                # Domain in override list + sensitive
                print(
                    "{}\t{}\t{}".format(domain, -2, 1) + "\n", end=""
                )  # score assumed to be 1
            else:
                # Domain is in override list and we have categories from taxonomy
                for c in topics:
                    print(
                        "{}\t{}\t{}".format(domain, c, 1) + "\n", end=""
                    )  # score assumed to be 1
        else:
            # If not call the classifier
            topics = config.web_model.classify(processed_domain)
            cats = sorted(
                topics.classifications[0].categories,
                key=lambda x: x.score,
                reverse=True,
            )[0 : config.web_max_topics]
            top_sum = 0
            unknown_score = None
            for c in cats:
                top_sum += c.score
                if int(c.category_name) == -2:
                    unknown_score = c.score
            if unknown_score and unknown_score / top_sum > config.web_min_unknown_score:
                print("{}\t{}\t{}".format(domain, -2, unknown_score) + "\n", end="")
                continue  # to next domain in for loop
            other = False
            for c in cats:
                if (
                    int(c.category_name) != -2
                    and c.score >= config.web_min_topic_score
                    and c.score / top_sum
                    >= config.web_min_normalized_score_within_top_n
                ):
                    other = True
                    print(
                        "{}\t{}\t{}".format(
                            domain,
                            c.category_name,
                            c.score,
                        )
                        + "\n",
                        end="",
                    )
            if not (other):
                if unknown_score:
                    print(
                        "{}\t{}\t{}".format(domain, -2, unknown_score) + "\n",
                        end="",
                    )
                else:
                    print("{}\t{}\t{}".format(domain, -2, 1) + "\n", end="")


if __name__ == "__main__":
    dependencies.load_all()

    if sys.argv[1] == "chrome_ml_model":
        domains = sys.argv[2:]
        chrome_ml_model(domains)

    elif sys.argv[1] == "chrome_ml_model_csv_header":
        utils.chrome_ml_model_csv_header()

    elif sys.argv[1] == "chrome_ml_model_csv":
        domains = sys.argv[2:]
        chrome_ml_model_csv(domains)

    elif sys.argv[1] == "chrome_csv_header":
        utils.chrome_csv_header()

    elif sys.argv[1] == "chrome_csv":
        domains = sys.argv[2:]
        chrome_csv(domains)

    else:
        raise ValueError("Incorrect argument passed to the function")

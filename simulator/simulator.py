import pandas as pd
import simulator_library
import numpy as np

import sys


def create_users(synthetic_users, nb_users):
    """Create users array"""
    users = []
    for i in range(nb_users):
        top5 = np.array(synthetic_users[i][1:6])
        users.append(StableUser(i, top5))
    return users


## USER CLASS
class StableUser:
    def __init__(self, id, top5):
        self.id = id
        self.top5 = top5
        self.one_shot_topics = []
        self.one_shot_ground_truth = []
        self.multi_shot_topics_a = None
        self.multi_shot_ground_truth_a = None
        self.multi_shot_denoise_pred_a = None
        self.multi_shot_genuine_topics_a = None
        self.multi_shot_observed_topics_a = None
        self.multi_shot_topics_b = None
        self.multi_shot_ground_truth_b = None
        self.multi_shot_denoise_pred_b = None
        self.multi_shot_genuine_topics_b = None
        self.multi_shot_observed_topics_b = None

    def one_shot_topics_call(self):
        """Simulate a one-shot call to TOPICS API"""
        topics, truth = simulator_library.topics_call(self.top5)
        for t in topics:
            self.one_shot_topics.append(t)
        for tr in truth:
            self.one_shot_ground_truth.append(tr)

    def one_shot_denoise_exp(self, noisy_topics_list, roc_curve=False):
        """Denoise one shot call (array of 3 topics)
        Return tp, fp, tn, fn"""
        if self.one_shot_topics == []:
            self.one_shot_topics_call()

        denoise_pred = simulator_library.one_shot_denoise(
            self.one_shot_topics,
            noisy_topics_list,
            roc_curve,
        )
        genuine = []
        for i in range(len(self.one_shot_topics)):
            if denoise_pred[i] == 1:
                genuine.append(self.one_shot_topics[i])
        tp, fp, tn, fn = simulator_library.compare_truth_denoise(
            self.one_shot_ground_truth, denoise_pred
        )
        intersection = list(set(self.top5).intersection(genuine))

        return tp, fp, tn, fn, len(intersection)

    def multi_shot_denoise_generate_a(self, nb_epochs, noisy_topics_list):
        """Generate what is needed for denoising and re-identification and
        return it"""
        if self.multi_shot_topics_a == None:
            (
                self.multi_shot_topics_a,
                self.multi_shot_ground_truth_a,
            ) = simulator_library.multi_shot_view_one_advertiser(self.top5, nb_epochs)

        if self.multi_shot_denoise_pred_a == None:
            (
                self.multi_shot_denoise_pred_a,
                self.multi_shot_genuine_topics_a,
                self.multi_shot_observed_topics_a,
            ) = simulator_library.multi_shot_denoise(
                self.multi_shot_topics_a, noisy_topics_list
            )

        return (
            self.id,
            self.multi_shot_topics_a,
            self.multi_shot_ground_truth_a,
            self.multi_shot_denoise_pred_a,
            self.multi_shot_genuine_topics_a,
            self.multi_shot_observed_topics_a,
        )

    def multi_shot_denoise_generate_b(self, nb_epochs, noisy_topics_list):
        """Generate what is needed for denoising and re-identification and
        return it"""
        if self.multi_shot_topics_b == None:
            (
                self.multi_shot_topics_b,
                self.multi_shot_ground_truth_b,
            ) = simulator_library.multi_shot_view_one_advertiser(self.top5, nb_epochs)

        if self.multi_shot_denoise_pred_b == None:
            (
                self.multi_shot_denoise_pred_b,
                self.multi_shot_genuine_topics_b,
                self.multi_shot_observed_topics_b,
            ) = simulator_library.multi_shot_denoise(
                self.multi_shot_topics_b, noisy_topics_list
            )

        return (
            self.id,
            self.multi_shot_topics_b,
            self.multi_shot_ground_truth_b,
            self.multi_shot_denoise_pred_b,
            self.multi_shot_genuine_topics_b,
            self.multi_shot_observed_topics_b,
        )


def gen_id(t1, t2, t3, t4, t5):
    topics = np.sort([t1, t2, t3, t4, t5])
    id = ""
    for t in topics:
        id += str(t) + "-"
    return id


def extract_stats_synthetic_datasets():
    paths = [
        "../output_web/simulator/52000_users/52000_users_domains.csv",
        "../output_web/simulator/250000_users/250000_users_domains.csv",
    ]

    for path in paths:
        df = pd.read_csv(path, sep="\t")
        df2 = pd.concat(
            [
                df["t1"],
                df["t2"],
                df["t3"],
                df["t4"],
                df["t5"],
            ]
        ).unique()
        print(len(df))
        print("Nb unique topics:")
        print(len(df2))
        df["id"] = df.apply(lambda x: gen_id(x.t1, x.t2, x.t3, x.t4, x.t5), axis=1)
        print("Nb unique profiles:")
        print(df["id"].nunique())
        print("====")


#######


def different_population_sizes(
    filename_users="output_web/simulator/synthetic/1k_users.csv",
):
    ## MULTI-SHOT EXPERIMENT (ONE SHOT is equal to epoch 0 observed only)
    min_nb_domains_in_top_1m = 10
    synthetic_topics = pd.read_csv(filename_users, sep="\t")
    synthetic_users = synthetic_topics.to_numpy()
    nb_users = len(synthetic_users)
    nb_epochs_total = 30
    users = create_users(synthetic_users, nb_users)
    noisy_topics_list = output_noisy_topics_traffic(crux_path, min_nb_domains_in_top_1m)

    simulator_library.multi_shot_denoise_generate_exp_a(
        users, noisy_topics_list, nb_epochs_total
    )
    simulator_library.multi_shot_denoise_generate_exp_b(
        users, noisy_topics_list, nb_epochs_total
    )
    simulator_library.multi_shot_denoise_results_exp_all_epochs_plot(
        users, nb_epochs_total
    )

    ## RE-IDENTIFICATION
    simulator_library.reidentification_all_epochs(users, nb_epochs_total)


if __name__ == "__main__":
    if sys.argv[1] == "classifier":
        if len(sys.argv) == 5:
            crux_path = sys.argv[2]
            users_topics_path = sys.argv[3]
            output_folder = sys.argv[4]

            # Thresholds and labels for ROC curve
            roc_thresholds = [0, 1, 2, 5, 10, 20, 50, 100, 500, 1000]
            roc_labels = ["0", "1", "2", "5", "10", "20", "50", "100", "500", "1k"]

            # Load data
            synthetic_topics = pd.read_csv(users_topics_path, sep="\t")
            synthetic_users = synthetic_topics.to_numpy()
            nb_users = len(synthetic_users)
            users = create_users(synthetic_users, nb_users)
            simulator_library.one_shot_denoise_roc_curve(
                crux_path, output_folder, roc_thresholds, roc_labels, users
            )
        else:
            raise ValueError("Incorrect number of arguments passed")

    elif sys.argv[1] == "denoise_and_reidentify":
        if len(sys.argv) == 5:
            crux_path = sys.argv[2]
            users_topics_path = sys.argv[3]
            output_folder = sys.argv[4]

            # Parameters for evaluation
            min_nb_domains_in_top_1m = 10
            nb_epochs_total = 30

            synthetic_topics = pd.read_csv(users_topics_path, sep="\t")
            synthetic_users = synthetic_topics.to_numpy()
            nb_users = len(synthetic_users)

            users = create_users(synthetic_users, nb_users)
            noisy_topics_list = simulator_library.output_noisy_topics_traffic(
                crux_path, min_nb_domains_in_top_1m
            )

            # Denoise
            simulator_library.multi_shot_denoise_generate_exp_a(
                users, noisy_topics_list, nb_epochs_total
            )
            simulator_library.multi_shot_denoise_generate_exp_b(
                users, noisy_topics_list, nb_epochs_total
            )
            simulator_library.multi_shot_denoise_results_exp_all_epochs(
                users, nb_epochs_total, output_folder
            )

            ## RE-IDENTIFICATION
            simulator_library.reidentification_all_epochs(
                users, nb_epochs_total, output_folder
            )

        else:
            raise ValueError("Incorrect number of arguments passed")

    elif sys.argv[1] == "plot":
        if len(sys.argv) == 4:
            output_folder = sys.argv[2]
            nb_users = int(sys.argv[3])

            simulator_library.plot_multi_shot_denoise(output_folder, 30)

            simulator_library.plot_min_median_max_nb_genuine_retrieved(
                output_folder, 30
            )
            epochs = [0, 1, 4, 9, 14, 19, 24, 29]
            simulator_library.plot_cdf_size_reidentified_groups(
                output_folder, epochs, nb_users
            )

        else:
            raise ValueError("Incorrect number of arguments passed")

    else:
        raise ValueError("Wrong argument passed")

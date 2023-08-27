import random as rd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from multiprocessing import Pool
import sim_utils
from itertools import repeat

sns.set_theme(style="darkgrid")


## HELPERS + POOL FUNCTIONS + EXP FUNCTIONS


def savefig(path, size=[4, 3]):
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.gcf().set_size_inches(*size)
    plt.tight_layout(
        pad=0,
    )
    plt.savefig(path, bbox_inches="tight")
    plt.clf()


def init_worker(noisy_topics_list, roc_curve):
    """Initializer for pool worker - pass global shared variable between
    workers"""
    global shared_noisy_topics_list
    shared_noisy_topics_list = noisy_topics_list
    global shared_roc_curve
    shared_roc_curve = roc_curve


def aggregate_denoise_results(results, print_results, output_file, threshold=10):
    """Aggregate the results returned by the pool of workers"""
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    intersection = []

    for result in results:
        true_positive += result[0]
        false_positive += result[1]
        true_negative += result[2]
        false_negative += result[3]
        intersection.append(result[4])

    true_positive_rate = (true_positive) / (true_positive + false_negative)
    false_positive_rate = (false_positive) / (false_positive + true_negative)

    df = pd.DataFrame({"intersection": np.array(intersection)})
    if print_results:
        with open(output_file, "a") as f:
            f.write("---Threshold {}---\n".format(threshold))
            f.write("true_positive: {}\n".format(true_positive))
            f.write("false_positive: {}\n".format(false_positive))
            f.write("true_negative: {}\n".format(true_negative))
            f.write("false_negative: {}\n".format(false_negative))
            f.write(
                "Accuracy: {}\n".format(
                    (true_positive + true_negative)
                    / (true_positive + true_negative + false_positive + false_negative)
                ),
            )
            f.write(
                "precision: {}\n".format(
                    (true_positive) / (true_positive + false_positive)
                )
            )
            f.write("recall/TPR: {}\n".format(true_positive_rate))
            f.write("FPR: {}\n".format(false_positive_rate))
            f.write("--")
            f.write("{}\n".format(df.describe()))

    return true_positive_rate, false_positive_rate, df["intersection"].median()


def plot_roc(tpr, fpr, labels, ratio_x, ratio_y, filename):
    """Plot roc curve"""
    plt.clf()
    data = pd.DataFrame({"TPR": tpr, "FPR": fpr})
    plot = sns.lineplot(data=data, x="FPR", y="TPR", marker="o")
    for i in range(len(labels)):
        plt.annotate(labels[i], (fpr[i] + ratio_x, tpr[i] + ratio_y))
    plt.tight_layout()
    savefig("figs/simulator/" + filename + "_roc_curve.pdf")


# One shot
def one_shot_denoise_pool_function(user):
    """Function executed by pool of workers"""
    global shared_noisy_topics_list
    global shared_roc_curve
    return user.one_shot_denoise_exp(shared_noisy_topics_list, shared_roc_curve)


def one_shot_denoise_roc_curve(thresholds, labels, users, roc_curve=True):
    """One shot ROC curve experiment: evaluate performance of classifier"""
    tpr = []
    fpr = []
    intersection_med = []
    for t in thresholds:
        noisy_topics_list = sim_utils.output_noisy_topics_traffic(t)
        with Pool(
            initializer=init_worker,
            initargs=(
                noisy_topics_list,
                roc_curve,
            ),
        ) as pool:
            results = pool.map(one_shot_denoise_pool_function, users)
            tpr_temp, fpr_temp, intersection_med_temp = aggregate_denoise_results(
                results,
                True,
                "figs/simulator/classifier_one_shot_denoise.stats",
                t,
            )
            tpr.append(tpr_temp)
            fpr.append(fpr_temp)
            intersection_med.append(intersection_med_temp)
    np.save("figs/simulator/classifier_tpr.npy", np.array(tpr))
    np.save("figs/simulator/classifier_fpr.npy", np.array(fpr))
    np.save(
        "figs/simulator/classifier_intersection_med.npy",
        np.array(intersection_med),
    )
    plot_roc(np.array(tpr), np.array(fpr), labels, -0.0003, 0.01, "classifier")


def one_shot_denoise_experiment(users, noisy_topics_list, roc_curve=False):
    """One shot denoise experiment"""
    with Pool(
        initializer=init_worker,
        initargs=(
            noisy_topics_list,
            roc_curve,
        ),
    ) as pool:
        results = pool.map(one_shot_denoise_pool_function, users)
    aggregate_denoise_results(
        results,
        True,
        "figs/simulator/one_shot_denoise_" + str(len(users)) + ".stats",
    )


# Multi-shot
def multi_shot_denoise_generate_a_pool_function(user, nb_epochs):
    """Executed by pool of workers"""
    global shared_noisy_topics_list
    return user.multi_shot_denoise_generate_a(nb_epochs, shared_noisy_topics_list)


def multi_shot_denoise_generate_b_pool_function(user, nb_epochs):
    """Executed by pool of workers"""
    global shared_noisy_topics_list
    return user.multi_shot_denoise_generate_b(nb_epochs, shared_noisy_topics_list)


def multi_shot_denoise_generate_exp(
    users, noisy_topics_list, nb_epochs, roc_curve=False
):
    """Generate what is needed for the multi-shot experiment and update
    objects"""
    multi_shot_denoise_generate_exp_a(users, noisy_topics_list, nb_epochs)
    multi_shot_denoise_generate_exp_b(users, noisy_topics_list, nb_epochs)


def multi_shot_denoise_generate_exp_a(
    users, noisy_topics_list, nb_epochs, roc_curve=False
):
    """Generate what is needed for the multi-shot experiment and update
    objects - A"""
    with Pool(
        initializer=init_worker,
        initargs=(noisy_topics_list, roc_curve),
    ) as pool:
        results = pool.starmap(
            multi_shot_denoise_generate_a_pool_function, zip(users, repeat(nb_epochs))
        )
    # collect results and update - serialization of objects with python
    # multiprocessing and pickle is a bad idea
    for r in results:
        id = r[0]
        users[id].multi_shot_topics_a = r[1]
        users[id].multi_shot_ground_truth_a = r[2]
        users[id].multi_shot_denoise_pred_a = r[3]
        users[id].multi_shot_genuine_topics_a = r[4]
        users[id].multi_shot_observed_topics_a = r[5]


def multi_shot_denoise_generate_exp_b(
    users, noisy_topics_list, nb_epochs, roc_curve=False
):
    """Generate what is needed for the multi-shot experiment and update
    objects - B"""
    with Pool(
        initializer=init_worker,
        initargs=(noisy_topics_list, roc_curve),
    ) as pool:
        results = pool.starmap(
            multi_shot_denoise_generate_b_pool_function, zip(users, repeat(nb_epochs))
        )
    # collect results and update - serialization of objects with python
    # multiprocessing and pickle is a bad idea
    for r in results:
        id = r[0]
        users[id].multi_shot_topics_b = r[1]
        users[id].multi_shot_ground_truth_b = r[2]
        users[id].multi_shot_denoise_pred_b = r[3]
        users[id].multi_shot_genuine_topics_b = r[4]
        users[id].multi_shot_observed_topics_b = r[5]


def multi_shot_denoise_specific_epoch_a_function_pool(user, epoch_index):
    """Function Pool for results of a specific epoch for A"""
    pred = user.multi_shot_denoise_pred_a[epoch_index]
    truth = user.multi_shot_ground_truth_a[epoch_index]
    genuine = user.multi_shot_genuine_topics_a[epoch_index]
    top5 = user.top5

    tp, fp, tn, fn = compare_truth_denoise(truth, pred)

    intersection = list(set(top5).intersection(genuine))

    return tp, fp, tn, fn, len(intersection)


def multi_shot_denoise_specific_epoch_b_function_pool(user, epoch_index):
    """Function Pool for results of a specific epoch for B"""
    pred = user.multi_shot_denoise_pred_b[epoch_index]
    truth = user.multi_shot_ground_truth_b[epoch_index]
    genuine = user.multi_shot_genuine_topics_b[epoch_index]
    top5 = user.top5

    tp, fp, tn, fn = compare_truth_denoise(truth, pred)

    intersection = list(set(top5).intersection(genuine))

    return tp, fp, tn, fn, len(intersection)


def multi_shot_denoise_results_exp_one_thread(users, epoch_index):
    results = np.zeros([len(users), 5])
    for i in range(len(users)):
        tp, fp, tn, fn, size_inter = multi_shot_denoise_specific_epoch_a_function_pool(
            users[i], epoch_index
        )
        results[i][0] = tp
        results[i][1] = fp
        results[i][2] = tn
        results[i][3] = fn
        results[i][4] = size_inter
    output_file = "figs/simulator/multi_shot_denoise_" + str(len(users)) + ".stats"
    with open(output_file, "a") as f:
        f.write("--Epoch: {} ---".format(epoch_index))
    return aggregate_denoise_results(results, True, output_file)


def multi_shot_denoise_results_exp_all_epochs_plot(users, nb_epochs_total):
    tp_rate = np.zeros(nb_epochs_total)
    fp_rate = np.zeros(nb_epochs_total)
    inter_meds = np.zeros(nb_epochs_total)
    for i in range(nb_epochs_total):
        (
            tp_rate[i],
            fp_rate[i],
            inter_meds[i],
        ) = multi_shot_denoise_results_exp_one_thread(users, i)
    np.save("figs/simulator/multi_shot_tpr.npy", tp_rate)
    np.save("figs/simulator/multi_shot_fpr.npy", fp_rate)
    np.save("figs/simulator/multi_shot_intersection.npy", inter_meds)

    multi_shot_denoise_plot_results()


def multi_shot_denoise_plot_results():
    tp_rate = np.load("figs/simulator/multi_shot_tpr.npy")
    fp_rate = np.load("figs/simulator/multi_shot_fpr.npy")
    nb_top5_recovered_median = np.load("figs/simulator/multi_shot_intersection.npy")
    x = [i + 1 for i in range(len(tp_rate))]
    labels = [str(i + 1) for i in range(len(tp_rate))]
    plot_roc(tp_rate, fp_rate, labels, 0.0001, 0.001, "multi_shot")

    plt.clf()
    data = pd.DataFrame({"x": x, "y": nb_top5_recovered_median})
    plot = sns.lineplot(data=data, x="x", y="y", marker="o")
    plot.set(xlabel="Epoch", ylabel="Median number genuine topics retrieved")
    plt.tight_layout()
    savefig("figs/simulator/multi_shot_nb_top5_recovered_median.pdf")


## RE-IDENTIFICATION


def reidentify_user_function_pool(one_user_view, user_id, reid_dict):
    """compare view to shared dictionary"""
    candidates = {}
    for t in one_user_view:
        for user_b_id in reid_dict[t]:
            if user_b_id in candidates.keys():
                candidates[user_b_id] += 1
            else:
                candidates[user_b_id] = 1

    keys = list(candidates.keys())
    values = list(candidates.values())

    if len(values) == 0:
        candidates_ids = []
    else:
        indices = [0]
        max_value = values[0]
        for i in range(1, len(values)):
            if values[i] > max_value:
                indices = [i]
                max_value = values[i]
            elif values[i] == max_value:
                indices.append(i)
        candidates_ids = [keys[i] for i in indices]

    # 0 means unsuccessfull, 1, means unique in your group (uniquely
    # re-identified!), higher values indicate that user is in a bigger group
    # (k-anonymity)
    if user_id not in candidates_ids:
        return 0
    else:
        return len(candidates_ids)


def aggregate_re_identification_results(results, epoch_index, filename):
    size_reidentified_groups = np.array(results)
    np.save(
        "figs/simulator/size_reidentified_groups_" + filename + ".npy",
        size_reidentified_groups,
    )
    nb_users = len(results)

    nb_users_re_identified = sum(size_reidentified_groups == 1)
    nb_users_failure = sum(size_reidentified_groups == 0)
    nb_users_better_chance = sum(size_reidentified_groups > 1)
    with open("figs/simulator/reid_" + filename + ".stats", "a") as f:
        f.write("Epoch --- {} ---\n".format(epoch_index))
        f.write(
            "Uniquely re-identified: {}  -  {}\n".format(
                nb_users_re_identified, nb_users_re_identified / nb_users
            )
        )
        f.write(
            "Failure re-identified: {}  -  {}\n".format(
                nb_users_failure, nb_users_failure / nb_users
            )
        )
        f.write(
            "Better chance re-identified: {}  -  {}\n".format(
                nb_users_better_chance, nb_users_better_chance / nb_users
            )
        )


def reidentification_specific_epoch(users, epoch_index):
    """
    First we generate the re-id dictionary
    When we have collected enough epochs, we see all genuine topics, but
    before that we do not have all of them, so we add the observed ones that
    we think are not noisy"""

    reid_dict = {}
    for t in range(350):
        reid_dict[t] = []

    view_a = []
    users_ids = np.arange(len(users))

    for user in users:
        genuine_b = user.multi_shot_genuine_topics_b[epoch_index]
        if len(genuine_b) >= 5:
            for topic in genuine_b:
                reid_dict[topic].append(user.id)
        else:
            observed_b = user.multi_shot_observed_topics_b[epoch_index]
            for topic in np.union1d(genuine_b, observed_b):
                reid_dict[topic].append(user.id)

        genuine_a = user.multi_shot_genuine_topics_a[epoch_index]
        if len(genuine_a) >= 5:
            view_a.append(genuine_a)
        else:
            observed_a = user.multi_shot_observed_topics_a[epoch_index]
            view_a.append(np.union1d(genuine_a, observed_a))

    with Pool() as pool:
        results = pool.starmap(
            reidentify_user_function_pool,
            zip(view_a, users_ids, repeat(reid_dict)),
        )
    aggregate_re_identification_results(
        results, epoch_index, str(len(users)) + "_users" + str(epoch_index) + "_epoch"
    )


def reidentification_all_epochs(users, nb_epochs_total):
    """Re-identification all epochs and save results to disk for later
    analysis/plots"""
    for epoch_index in range(nb_epochs_total):
        reidentification_specific_epoch(users, epoch_index)


## TOPICS CALL
def topics_call(top5, one_shot=True, output_previous=None, ground_truth_previous=None):
    """Simulate a call to TOPICS API one-shot and multi-shot
    for multi-shot: pass output (topics + ground trtuh) of previous epoch,
    returned array is not shuffled randomly to make it easier to keep track for
    the consecutive calls for multi-shot. This has no further impact as
    denoising is done as if this array was shuffled.
    """
    p = 0.05

    if one_shot:
        output = []
        ground_truth = []
    else:
        # keep the same as output before / at most learn 1 new one
        output = [output_previous[1], output_previous[2]]
        ground_truth = [ground_truth_previous[1], ground_truth_previous[2]]

    for i in range(3 - len(output)):
        if rd.random() < p:
            t = rd.randrange(1, 349 + 1)
            gt = 0  # noisy
        else:
            t = np.random.choice(top5, 1)[0]
            gt = 1  # genuine
        output.append(t)
        ground_truth.append(gt)
    return np.array(output), np.array(ground_truth)


def multi_shot_view_one_advertiser(top5, nb_epochs):
    """First epoch we see 3 topics, then subsequent calls, return 2 topics
    we already observed + 1 new one"""
    view = np.empty(shape=(nb_epochs, 3), dtype="int")
    truth = np.empty(shape=(nb_epochs, 3), dtype="int")

    output_previous, ground_truth_previous = topics_call(top5)
    view[0] = output_previous
    truth[0] = ground_truth_previous

    for i in range(nb_epochs - 1):
        output_previous, ground_truth_previous = topics_call(
            top5, False, output_previous, ground_truth_previous
        )
        view[i + 1] = output_previous
        truth[i + 1] = ground_truth_previous

    return view, truth


## DENOISING
def flag_noisy_topics(topics_output, noisy_topics_list):
    """Output = array with 0 if topic is in noisy list, 1 if not"""
    denoise_pred = np.ones(len(topics_output))
    for i in range(len(topics_output)):
        if topics_output[i] in noisy_topics_list:
            denoise_pred[i] = 0
    return denoise_pred


def compare_truth_denoise(ground_truth, denoise_pred):
    """
    Compute true positive, false positive, etc. positive class = noisy negative
    class = genuine
    """
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    assert len(ground_truth) == len(denoise_pred)
    for i in range(len(ground_truth)):
        if ground_truth[i] == denoise_pred[i]:
            # positive class = noisy negative class = genuine
            if ground_truth[i] == 0:
                tp += 1
            else:
                tn += 1
        else:
            if ground_truth[i] == 0:
                fp += 1
            else:
                fn += 1
    return tp, fp, tn, fn


def one_shot_denoise(output_one_shot, noisy_topics_list, roc_curve=False):
    """Denoise output_one_shot with comparison to noisy topics list
    if roc_curve we avoid looking at repetitions
    """
    denoise_pred = flag_noisy_topics(output_one_shot, noisy_topics_list)
    if not (roc_curve):
        # check for repetitions
        if output_one_shot[0] == output_one_shot[1]:
            denoise_pred[0] = 1
            denoise_pred[1] = 1

        if output_one_shot[0] == output_one_shot[2]:
            denoise_pred[0] = 1
            denoise_pred[2] = 1

        if output_one_shot[1] == output_one_shot[2]:
            denoise_pred[1] = 1
            denoise_pred[2] = 1

    return denoise_pred


def multi_shot_pred(topics_temp, genuine_temp, noisy_topics_list):
    """Helper function for multi shot denoising"""
    # Case 1: check if we have top 5 stable already, if so everything is noisy except
    # the ones we have in genuine_Temp
    if len(genuine_temp) >= 5:
        denoise_pred_temp = np.zeros(len(topics_temp))
    # Case 2: if we do not have top5, everything is considered genuine except topics in
    # noisy list
    else:
        denoise_pred_temp = flag_noisy_topics(topics_temp, noisy_topics_list)
    # we check if in genuine_temp and we set to genuine. We do that after, so
    # that for case 2 in case we flagged as noisy a topic that is genuine, we
    # revert it here
    for i in range(len(topics_temp)):
        if topics_temp[i] in genuine_temp:
            denoise_pred_temp[i] = 1

    return denoise_pred_temp


def multi_shot_denoise(view, noisy_topics_list):
    """
    Perform denoising over epochs, store denoise prediction, genuine topics, and
    observed topics along each epoch, so that we can just reuse those for re-identification
    """
    nb_epochs = len(view)

    topic_ids = set(view.flatten())

    genuine_topics = []
    observed_topics_not_noisy = []
    denoise_pred = []
    # dictionary to hold first time seen and last time seen for each topic
    topics = {}
    for t in topic_ids:
        topics[t] = None

    # repetitions in output for 1st epoch?
    topics_temp = view[0]
    genuine_temp = []

    if topics_temp[0] == topics_temp[1] or topics_temp[0] == topics_temp[2]:
        genuine_temp.append(topics_temp[0])

    if topics_temp[1] == topics_temp[2]:
        genuine_temp.append(topics_temp[1])
    # init first/last time seen
    for t in topics_temp:
        topics[t] = [0, 0]
    # collect genuine topics
    genuine_topics.append(list(set(genuine_temp)))
    # collect topics observed but deemed not noisy
    observed_temp = []
    for t in list(set(topics_temp).difference(set(genuine_temp))):
        if t not in noisy_topics_list:
            observed_temp.append(t)
    observed_topics_not_noisy.append(list(set(observed_temp)))
    # prediction for this epoch
    denoise_pred.append(multi_shot_pred(topics_temp, genuine_temp, noisy_topics_list))

    # go through the array and record first time seen, last time seen
    # check for genuine topics
    # update observed array of topics
    for i in range(1, nb_epochs):
        topics_temp = view[i]
        genuine_temp = genuine_topics[i - 1].copy()
        observed_temp = observed_topics_not_noisy[i - 1].copy()

        for t in topics_temp:
            # if not identified as genuine already
            if t not in genuine_temp:
                # if already set in dictionary, compare to first and last time
                # for non consecutive repetitions
                if topics[t]:
                    if topics[t][0] + 3 <= i:
                        genuine_temp.append(t)
                    elif topics[t][1] != i - 1:
                        genuine_temp.append(t)
                    topics[t][1] = i
                # set dictionary and first/last time seen
                else:
                    topics[t] = [i, i]

        # collect genuine topics
        genuine_topics.append(list(set(genuine_temp)))
        # collect topics observed but deemed not noisy
        for t in list(set(topics_temp).difference(set(genuine_temp))):
            if t not in noisy_topics_list:
                observed_temp.append(t)
        observed_topics_not_noisy.append(
            list(set(observed_temp).difference(set(genuine_temp)))
        )
        # prediction for this epoch
        denoise_pred.append(
            multi_shot_pred(topics_temp, genuine_temp, noisy_topics_list)
        )

    return denoise_pred, genuine_topics, observed_topics_not_noisy


## Plot functions


def plot_multi_shot_denoise(nb_epochs_total, results_dict):
    epochs = [i + 1 for i in range(nb_epochs_total)]
    data = pd.DataFrame(
        {
            "Epochs": epochs,
            "Accuracy": results_dict["Accuracy"],
            "Precision": results_dict["Precision"],
            "TPR": results_dict["TPR"],
            "FPR": results_dict["FPR"],
        }
    )
    plt.clf()
    ax = sns.lineplot(
        data=data,
        x="Epochs",
        y="Accuracy",
        marker="o",
        color="#005AB5",
        linewidth=3,
        label="Accuracy",
    )
    ax.set_ylabel("Accuracy", color="#005AB5")
    # ax.lines[0].set_linestyle("--")

    ax2 = ax.twinx()
    sns.lineplot(
        data=data,
        x="Epochs",
        y="Precision",
        ax=ax2,
        marker="P",
        color="#D41159",
        label="Precision",
    )
    ax2.set_ylabel("Precision", color="#D41159")
    ax2.grid(None)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.get_legend().remove()
    ax.legend(h1 + h2, l1 + l2)
    ax2.get_legend().remove()
    plt.tight_layout()
    savefig("figs/simulator/multi_shot_denoise_accuracy_precision.pdf")

    plt.clf()
    ax = sns.lineplot(
        data=data, x="Epochs", y="FPR", marker="o", color="#1AFF1A", label="FPR"
    )

    ax.set_ylabel("FPR", color="#1AFF1A")

    ax2 = ax.twinx()
    sns.lineplot(
        data=data, x="Epochs", y="TPR", ax=ax2, marker="P", color="#4B0092", label="TPR"
    )
    ax2.set_ylabel("TPR", color="#4B0092")
    ax2.grid(None)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.get_legend().remove()
    ax2.get_legend().remove()
    ax.legend(h1 + h2, l1 + l2, loc="center right")
    plt.tight_layout()
    savefig("figs/simulator/multi_shot_denoise_tpr_fpr.pdf")


def plot_cdf_size_reidentified_groups(nb_users):
    df = pd.DataFrame(columns=["k", "Epochs"])
    epochs = [0, 1, 4, 9, 14, 19, 24, 29]

    for epoch in epochs:
        filename = (
            "figs/simulator/size_reidentified_groups_"
            + str(nb_users)
            + "_users"
            + str(epoch)
            + "_epoch.npy"
        )

        size_epoch = np.load(filename)
        df = pd.concat(
            [df, pd.DataFrame({"k": size_epoch, "Epochs": epoch + 1})],
            ignore_index=True,
        )
    df["k"] = df["k"].replace(0, nb_users)
    plt.clf()
    plot = sns.ecdfplot(
        data=df,
        x="k",
        stat="proportion",
        hue="Epochs",
    )
    sns.move_legend(
        plot,
        "upper left",
        bbox_to_anchor=(1, 1),
        ncol=1,
        title="Epochs",
        frameon=False,
        reverse=True,
    )
    plot.set(xlabel="$k$", ylabel="Proportion of users")
    plot.set_xscale("symlog")
    plot.set_xlim([0.8, nb_users * 1.2])
    savefig("figs/simulator/cdf_size_groups_" + str(nb_users) + ".pdf")


def plot_median_nb_genuine_retrieved(median):
    epochs = [i + 1 for i in range(30)]
    data = pd.DataFrame({"median": median, "Epochs": epochs})
    plt.clf()
    plot = sns.lineplot(data=data, x="Epochs", y="median", marker="o")
    plot.set(ylabel="Median size of top 5 retrieved")
    savefig("figs/simulator/median_nb_genuine_topics.pdf")

import config
import dependencies
import analysis

import os
import pandas as pd
import re
import sys


if __name__ == "__main__":
    if sys.argv[1] == "plots_and_stats":
        # Pass as input the folder where the classification of the corresponding
        # list is stored
        output_folder = sys.argv[2]
        chrome_csv = output_folder + config.chrome_file

        # Check if filter was already applied during classification (i.e., if
        # file already exists)
        if not (os.path.isfile(chrome_csv)):
            df_not_filtered = analysis.read_classified_csv(
                output_folder + config.chrome_ml_model_file
            )
            df = analysis.chrome_filter(df_not_filtered, chrome_csv)
        else:
            df = analysis.read_chrome_csv(chrome_csv)

        # Plot graphs in figs/ folder and extract stats
        analysis.graph_describe_all(df, output_folder)

    elif sys.argv[1] == "compare_override_to_static":
        # Pass as input the folder where the classification of override is
        # stored and where to save the graphs and stats for the static mapping
        # annotated by Google
        override_output_folder = sys.argv[2]
        static_output_folder = sys.argv[3]

        dependencies.load_all()

        # Extract static mapping annotated by google
        df_static = analysis.override_create_df()
        # Plot and stats for static mapping
        analysis.graph_describe_all(df_static, static_output_folder)
        # Extract also stats about the taxonomy
        analysis.taxonomy(static_output_folder)

        # Same top nb of topics as in static mapping
        df_override = analysis.read_classified_csv(
            override_output_folder + config.chrome_ml_model_file
        )
        analysis.compare_to_ground_truth(
            df_static, df_override, static_output_folder, "same_nb_as_static", True
        )
        analysis.results_model_ground_truth(
            df_static, static_output_folder, "same_nb_as_static"
        )

        # Applying chrome filter
        df_override_chrome = analysis.read_chrome_csv(
            override_output_folder + config.chrome_file
        )
        analysis.compare_to_ground_truth(
            df_static,
            df_override_chrome,
            static_output_folder,
            "chrome_filtering",
            False,
        )
        analysis.results_model_ground_truth(
            df_static, static_output_folder, "chrome_filtering"
        )

    elif sys.argv[1] == "compare_to_cloudflare":
        topics_path = sys.argv[2]
        cloudflare_path = sys.argv[3]
        mapping_path = sys.argv[4]
        output_folder = sys.argv[5]
        output_dict_path = sys.argv[6]
        crux_dependencies_path = sys.argv[7]

        dependencies.load_all()

        # Cloudflare comparison
        # Need manual mapping of topics
        if not (os.path.isfile(output_dict_path)):
            analysis.parse_cloudflare_topics_mapping(
                mapping_path, output_dict_path
            )

        # compare to static mapping released by Google
        df_static = analysis.override_create_df()
        df_cloudflare = pd.read_csv(cloudflare_path, sep="\t")
        df_cloudflare["domain"] = df_cloudflare["domain"].apply(
            lambda x: re.sub(r"[^a-zA-Z0-9]+", " ", x)
        )
        df_c = pd.merge(df_static, df_cloudflare, on="domain", how="inner")

        filename_static = "static"
        analysis.compare_topics_to_cloudflare(
            df_static,
            df_c,
            output_folder,
            filename_static,
            crux_dependencies_path,
            output_dict_path,
        )
        analysis.describe_results_cloudflare_comparison(
            output_folder, filename_static
        )

        # Compare to crux classification
        filename_crux = "1M"
        df_crux_chrome = pd.read_csv(topics_path, sep="\t")
        df_cloudflare = pd.read_csv(cloudflare_path, sep="\t")
        analysis.compare_topics_to_cloudflare(
            df_crux_chrome,
            df_cloudflare,
            output_folder,
            filename_crux,
            crux_dependencies_path,
            output_dict_path,
            True,
        )
        for r in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
            analysis.describe_results_cloudflare_comparison(
                output_folder, filename_crux, r
            )

    elif sys.argv[1] == "manual_verification":
        if len(sys.argv) != 5:
            raise ValueError(
                "Wrong number of arguments passed to this script: needs to be nb_domains_to_manually_verify, path_to_crux_classified_by_topics, output_folder"
            )
        else:
            nb_domains = int(sys.argv[2])
            path_crux = sys.argv[3]
            output_folder = sys.argv[4]

            output_sample = output_folder + "/sample.jsonl"
            output_augmented = output_folder + "/augmented_sample.jsonl"
            output_verified = output_folder + "/verified_sample.jsonl"

            dependencies.load_all()

            df_crux_chrome = pd.read_csv(path_crux, sep="\t")

            analysis.crux_extract_sample_size_x(
                df_crux_chrome, nb_domains, output_sample
            )

            if not (os.path.isfile(output_augmented)):
                # /!\ WARNING /!\
                # the following call make http requests to random websites, you may
                #   want to use a VPN for that
                analysis.crux_augment_with_meta_description(
                    output_sample, output_augmented
                )
            # manual verification
            analysis.crux_verification(output_augmented, output_verified)

    else:
        raise ValueError("Incorrect argument passed to the function")

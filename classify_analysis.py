import config
import dependencies
import analysis_library

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
            df_not_filtered = analysis_library.read_classified_csv(
                output_folder + config.chrome_ml_model_file
            )
            df = analysis_library.chrome_filter(df_not_filtered, chrome_csv)
        else:
            df = analysis_library.read_chrome_csv(chrome_csv)

        # Plot graphs in figs/ folder and extract stats
        analysis_library.graph_describe_all(df, output_folder)

    elif sys.argv[1] == "compare_override_to_static":
        # Pass as input the folder where the classification of override is
        # stored and where to save the graphs and stats for the static mapping
        # annotated by Google
        override_output_folder = sys.argv[2]
        static_output_folder = sys.argv[3]

        dependencies.load_all()

        # Extract static mapping annotated by google
        df_static = analysis_library.override_create_df()
        # Plot and stats for static mapping
        analysis_library.graph_describe_all(df_static, static_output_folder)
        # Extract also stats about the taxonomy
        analysis_library.taxonomy(static_output_folder)

        # Same top nb of topics as in static mapping
        df_override = analysis_library.read_classified_csv(
            override_output_folder + config.chrome_ml_model_file
        )
        analysis_library.compare_to_ground_truth(
            df_static, df_override, static_output_folder, "same_nb_as_static", True
        )
        analysis_library.results_model_ground_truth(
            df_static, static_output_folder, "same_nb_as_static"
        )

        # Applying chrome filter
        df_override_chrome = analysis_library.read_chrome_csv(
            override_output_folder + config.chrome_file
        )
        analysis_library.compare_to_ground_truth(
            df_static,
            df_override_chrome,
            static_output_folder,
            "chrome_filtering",
            False,
        )
        analysis_library.results_model_ground_truth(
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
            analysis_library.parse_cloudflare_topics_mapping(
                mapping_path, output_dict_path
            )

        # compare to static mapping released by Google
        df_static = analysis_library.override_create_df()
        df_cloudflare = pd.read_csv(cloudflare_path, sep="\t")
        df_cloudflare["domain"] = df_cloudflare["domain"].apply(
            lambda x: re.sub(r"[^a-zA-Z0-9]+", " ", x)
        )
        df_c = pd.merge(df_static, df_cloudflare, on="domain", how="inner")

        analysis_library.compare_topics_to_cloudflare(
            df_static,
            df_c,
            output_folder,
            "override",
            crux_dependencies_path,
            output_dict_path,
        )
        analysis_library.describe_results_cloudflare_comparison(
            output_folder, "override"
        )

        # Compare to crux classification
        df_crux_chrome = pd.read_csv(topics_path, sep="\t")
        df_cloudflare = pd.read_csv(cloudflare_path, sep="\t")
        analysis_library.compare_topics_to_cloudflare(
            df_crux_chrome,
            df_cloudflare,
            output_folder,
            "1M",
            crux_dependencies_path,
            output_dict_path,
            True,
        )
        for r in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
            analysis_library.describe_results_cloudflare_comparison(
                output_folder, "1M", r
            )

    else:
        raise ValueError("Incorrect argument passed to the function")

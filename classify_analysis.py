import config
import dependencies
import analysis_library

import os
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

    else:
        raise ValueError("Incorrect argument passed to the function")

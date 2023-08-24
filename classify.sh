#!/bin/bash

if [[ "$1" == 'chrome' ]] || [[ "$1" == 'chrome_ml_model_top' ]] || [[ "$1" == 'chrome_ml_model_st' ]] || [[ "$1" == 'chrome_ml_model' ]] || [[ "$1" == 'chrome_ml_model_csv_header' ]] || [[ "$1" == 'chrome_ml_model_csv' ]] || [[ "$1" == 'chrome_csv_header' ]] || [[ "$1" == 'chrome_csv' ]]
then
    python3 process.py "$@"
else
    echo "First argument should specify classification type:
        - `chrome`: check in override_list (static mapping) and if not present top 5
            from ml_model (follows Colab example released by Google)
        - `chrome_ml_model_top`: run ml_model, output only top T, where T is passed as 2nd
            parameter to script
        - `chrome_ml_model_st`: run ml_model, output categories with score >= st, where st is passed as 2nd
            parameter to script
        - `chrome_ml_model`: run ml_model with filtering strategy used in Google Chrome Beta
        - `chrome_ml_model_csv_header`: output csv header for chrome_ml_model_csv option
        - `chrome_ml_model_csv`: run ml_model directly (no check against override_list and no
            filtering of output)
        - `chrome_csv_header`: output csv header for chrome_csv option
        - `chrome_csv`: run chrome classification (first check against override list,
            if not present run ml model, and filter output of model with Chrome beta
            filtering strategy)
fi

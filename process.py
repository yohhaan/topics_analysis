import dependencies
import inference
import utils

import sys

if __name__ == "__main__":
    dependencies.load_all()

    if sys.argv[1] == "chrome":
        domains = sys.argv[2:]
        inference.chrome(domains)

    elif sys.argv[1] == "chrome_ml_model_top":
        topT = sys.argv[2]
        domains = sys.argv[3:]
        inference.chrome_ml_model_top(domains, int(topT))

    elif sys.argv[1] == "chrome_ml_model_st":
        st = sys.argv[2]
        domains = sys.argv[3:]
        inference.chrome_ml_model_st(domains, float(st))

    elif sys.argv[1] == "chrome_ml_model":
        domains = sys.argv[2:]
        inference.chrome_ml_model(domains)

    elif sys.argv[1] == "chrome_ml_model_csv_header":
        utils.chrome_ml_model_csv_header()

    elif sys.argv[1] == "chrome_ml_model_csv":
        domains = sys.argv[2:]
        inference.chrome_ml_model_csv(domains)

    elif sys.argv[1] == "chrome_csv_header":
        utils.chrome_csv_header()

    elif sys.argv[1] == "chrome_csv":
        domains = sys.argv[2:]
        inference.chrome_csv(domains)

    else:
        raise ValueError("Incorrect argument passed to the function")

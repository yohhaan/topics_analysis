import config
import sandbox_dependencies.topics_web.page_topics_override_list_pb2 as page_topics_override_list_pb2

import math
import pickle
import pandas as pd
from tflite_support.task import core
from tflite_support.task import text


# Web
def load_web_override_list(path=config.web_override_list_path):
    # Load manually curated list
    config.web_override_list = page_topics_override_list_pb2.PageTopicsOverrideList()
    with open(path, "rb") as f:
        config.web_override_list.ParseFromString(f.read())


def load_web_taxonomy(path=config.web_taxonomy_path):
    # Load taxonomy
    with open(path, "rb") as f:
        config.web_taxonomy = pickle.load(f)


def load_web_model(path=config.web_model_path):
    # Load model
    options = text.BertNLClassifierOptions(
        base_options=core.BaseOptions(file_name=path)
    )

    config.web_model = text.BertNLClassifier.create_from_options(options)


def load_web():
    load_web_override_list()
    load_web_taxonomy()
    load_web_model()


def load_all():
    load_web()


if __name__ == "__main__":
    load_all()

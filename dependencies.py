import config
import sandbox_dependencies.topics.page_topics_override_list_pb2 as page_topics_override_list_pb2

import pickle
from tflite_support.task import core
from tflite_support.task import text


def load_override_list(path=config.override_list_path):
    # Load manually curated list
    config.override_list = page_topics_override_list_pb2.PageTopicsOverrideList()
    with open(path, "rb") as f:
        config.override_list.ParseFromString(f.read())


def load_taxonomy(path=config.taxonomy_path):
    # Load taxonomy
    with open(path, "rb") as f:
        config.taxonomy = pickle.load(f)


def load_model(path=config.model_path):
    # Load model
    options = text.BertNLClassifierOptions(
        base_options=core.BaseOptions(file_name=path)
    )

    config.model = text.BertNLClassifier.create_from_options(options)


def load_all():
    load_override_list()
    load_taxonomy()
    load_model()


if __name__ == "__main__":
    load_all()

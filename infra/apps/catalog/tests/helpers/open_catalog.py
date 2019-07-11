import os

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")


def open_catalog(file_name):
    return open(os.path.join(SAMPLES_DIR, file_name))

import os
import time
import json


def save_scores(high_scores, score_filepath):
    print("save_score")
    if os.access(score_filepath, os.W_OK):
        os.rename(score_filepath, score_filepath + "." + str(time.time()))
    with open(score_filepath, mode="w", encoding="utf-8") as f:
        json.dump(high_scores, f, indent=2)


def load_scores(score_filepath):
    print("load_score")
    if os.access(score_filepath, os.R_OK):
        print("open")
        with open(score_filepath, "r", encoding="utf-8") as f:
            return json.load(f)

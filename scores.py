import os
import time
import json

import datetime as dt

from dataclasses import dataclass, asdict, field
from typing import List, Dict

from random_username.generate import generate_username

SCORE_CATEGORIES = ["Product", "F&A", "Ops"]

DEFAULT_RAW_HIGH_SCORES = {
    cat: [
        {
            "username": generate_username(1)[0],
        }
    ]
    for cat in SCORE_CATEGORIES
}


@dataclass
class UserScore:
    username: str
    highest_score: int = 0
    latest_game: str = field(default_factory=lambda: str(dt.datetime.now()))
    n_games: int = 1


def sort_by_score(user_scores: List[UserScore]):
    return sorted(user_scores, key=lambda score: score.highest_score, reverse=True)


class ScoreRepository:
    def __init__(self, filepath: str):
        self.filepath = filepath
        raw_scores = load_scores(filepath) or DEFAULT_RAW_HIGH_SCORES
        self._scores: Dict[str, UserScore] = self._from_raw_scores(raw_scores)
        self._sort_scores()

    def _sort_scores(self):
        for cat, user_scores in list(self._scores.items()):
            self._scores[cat] = sort_by_score(user_scores)

    def save_to_file(self):
        raw_scores = self._to_raw_scores(self._scores)
        save_scores(raw_scores, self.filepath)

    @property
    def get_highest_scores_by_cat(self) -> Dict[str, UserScore]:
        return {cat: scores[0] for cat, scores in self._scores.items()}

    def update_user_score(self, cat, username, score) -> None:
        existing_user_score = next(
            (uc for uc in self._scores[cat] if uc.username == username), None
        )
        if existing_user_score:
            existing_user_score.n_games += 1
            existing_user_score.highest_score = max(
                existing_user_score.highest_score, score
            )
            existing_user_score.latest_game = str(dt.datetime.now())
        else:
            new_score = UserScore(username=username, highest_score=score)
            self._scores[cat].append(new_score)
            self._scores[cat] = sort_by_score(self._scores[cat])

        self.save_to_file()

    @staticmethod
    def _from_raw_scores(raw_scores: dict) -> dict:
        return {
            score_cat: [UserScore(**uc) for uc in user_scores]
            for score_cat, user_scores in raw_scores.items()
        }

    @staticmethod
    def _to_raw_scores(raw_scores: dict) -> dict:
        return {
            score_cat: [asdict(uc) for uc in user_scores]
            for score_cat, user_scores in raw_scores.items()
        }


def save_scores(high_scores: dict, score_filepath: str) -> None:
    print("save_score")
    if os.access(score_filepath, os.W_OK):
        os.rename(score_filepath, score_filepath + "." + str(time.time()))
    with open(score_filepath, mode="w", encoding="utf-8") as f:
        json.dump(high_scores, f, indent=2)


def load_scores(score_filepath):
    if os.access(score_filepath, os.R_OK):
        with open(score_filepath, "r", encoding="utf-8") as f:
            print("Load existing scores")
            return json.load(f)
    print("No existing scores found")

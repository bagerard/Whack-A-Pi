import os
import time
import json

import datetime as dt

from dataclasses import dataclass, asdict, field
from itertools import chain
from typing import List, Dict, Iterable

from random_username.generate import generate_username

SCORE_CATEGORIES = ["Product", "F&A", "Ops"]

DEFAULT_RAW_HIGH_SCORES = {
    cat: [
        {
            "username": generate_username(1)[0][:12],
        }
    ]
    for cat in SCORE_CATEGORIES
}


@dataclass
class UserScore:
    username: str
    highest_score: int = 0
    best_mean_hit_time: float = 100
    latest_game: str = field(default_factory=lambda: str(dt.datetime.now()))
    n_games: int = 1

    def pretty_dict(self):
        return {
            "username": self.username,
            "highest score": self.highest_score,
            "n games": self.n_games,
            "latest game": self.latest_game[:10],
            "best mean hit time": round(self.best_mean_hit_time, 2),
        }

    def register_new_game_score(self, score, mean_hit_time):
        self.n_games += 1
        self.highest_score = max(
            self.highest_score, score
        )
        self.latest_game = str(dt.datetime.now())
        best_mean_hit_time = min(
            self.best_mean_hit_time, mean_hit_time
        )
        self.best_mean_hit_time = round(best_mean_hit_time, 2)


def sort_by_score(user_scores: Iterable[UserScore]):
    """Sort an array of UserScores, highest first"""
    return sorted(user_scores, key=lambda score: score.highest_score, reverse=True)


def sort_by_latest_game(user_scores: Iterable[UserScore]):
    """Sort an array of UserScores, most recent first"""
    return sorted(user_scores, key=lambda score: score.latest_game, reverse=True)


class ScoreRepository:
    def __init__(self, filepath: str, backup_files: bool):
        self.filepath = filepath
        self.backup_files = backup_files
        raw_scores = load_scores(filepath) or DEFAULT_RAW_HIGH_SCORES
        self._scores: Dict[str, List[UserScore]] = self._from_raw_scores(raw_scores)
        self._sort_scores()

    @property
    def recent_gamers_usernames(self):
        return [uc.username for uc in sort_by_latest_game(self.all_user_scores)]

    @property
    def all_user_scores(self):
        return chain(*self._scores.values())

    @property
    def ranked_user_scores(self):
        return sort_by_score(self.all_user_scores)

    def _sort_scores(self):
        for cat, user_scores in list(self._scores.items()):
            self._scores[cat] = sort_by_score(user_scores)

    def save_to_file(self):
        raw_scores = self._to_raw_scores(self._scores)
        save_scores(raw_scores, self.filepath, backup_files=self.backup_files)

    @property
    def get_highest_scores_by_cat(self) -> Dict[str, UserScore]:
        return {cat: scores[0] for cat, scores in self._scores.items()}

    @property
    def overall_champion(self) -> Dict[str, UserScore]:
        return sort_by_score(self.get_highest_scores_by_cat.values())[0]

    def update_user_score(
        self, cat: str, username: str, score: int, mean_hit_time: float
    ) -> None:
        existing_user_score: UserScore = next(
            (uc for uc in self._scores[cat] if uc.username == username), None
        )
        if existing_user_score:
            existing_user_score.register_new_game_score(score=score, mean_hit_time=mean_hit_time)
        else:
            new_score = UserScore(
                username=username, highest_score=score, best_mean_hit_time=mean_hit_time
            )
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


def save_scores(high_scores: dict, score_filepath: str, backup_files: bool) -> None:
    print("save_score")
    if backup_files and os.access(score_filepath, os.W_OK):
        os.rename(score_filepath, score_filepath + "." + str(time.time()))
    with open(score_filepath, mode="w", encoding="utf-8") as f:
        json.dump(high_scores, f, indent=2)


def load_scores(score_filepath):
    if os.access(score_filepath, os.R_OK):
        with open(score_filepath, encoding="utf-8") as f:
            print("Load existing scores")
            return json.load(f)
    print("No existing scores found")

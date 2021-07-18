import os
import time
import json

import datetime as dt
from collections import defaultdict

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
        self.highest_score = max(self.highest_score, score)
        self.latest_game = str(dt.datetime.now())
        self.best_mean_hit_time = min(self.best_mean_hit_time, mean_hit_time)

    def merge(self, other_user_score: 'UserScore'):
        self.n_games += other_user_score.n_games
        self.highest_score = max(self.highest_score, other_user_score.highest_score)
        self.latest_game = max(self.latest_game, other_user_score.latest_game)
        self.best_mean_hit_time = min(self.best_mean_hit_time, other_user_score.best_mean_hit_time)


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
    def all_user_scores(self):
        return chain(*self._scores.values())

    @property
    def recent_user_scores(self):
        return sort_by_latest_game(self.all_user_scores)

    @property
    def recent_gamers_usernames(self):
        return [uc.username for uc in self.recent_user_scores]

    @property
    def ranked_user_scores(self):
        return sort_by_score(self.all_user_scores)

    def _sort_scores(self):
        for cat, user_scores in list(self._scores.items()):
            self._scores[cat] = sort_by_score(user_scores)

    def clean_scores(self):
        username_2_scores = defaultdict(dict)    # {username: {cat: user_score}}
        for cat, user_scores in self._scores.items():
            for user_score in user_scores:
                username_2_scores[user_score.username][cat] = user_score

        print("username_2_scores", username_2_scores)
        for username, cat_user_scores in username_2_scores.items():
            if len(cat_user_scores) > 1:
                print(f'Found duplicate record for {username}')

                details = [(cat, us.latest_game, us) for cat, us in cat_user_scores.items()]
                recent_details = sorted(details, key=lambda i: i[1], reverse=True)
                most_recent_user_score_cat = recent_details[0][0]
                most_recent_user_score = recent_details[0][2]
                print(f"Found most recent in {most_recent_user_score_cat}")

                for other_cat, _, dup_user_score in recent_details[1:]:
                    # Modify most recent record
                    most_recent_user_score.merge(dup_user_score)
                    # Remove older duplicates
                    print(f"cleaning {other_cat}")
                    self._scores[other_cat] = [us for us in self._scores[other_cat] if us is not dup_user_score]

    def save_to_file(self):
        self.clean_scores()
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
            existing_user_score.register_new_game_score(
                score=score, mean_hit_time=mean_hit_time
            )
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

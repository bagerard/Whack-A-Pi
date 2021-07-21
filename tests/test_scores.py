import datetime

import pytest

from scores import UserScore

TODAY = datetime.datetime.now()
YESTERDAY = TODAY - datetime.timedelta(days=1)


@pytest.fixture
def user_score():
    return UserScore(
        username="garbage1",
        highest_score=100,
        best_mean_hit_time=0.1,
        n_games=5,
        latest_game=YESTERDAY,
    )


def test_merge_score(user_score):
    init_n_game = user_score.n_games
    best_recent_score = UserScore(
        username=user_score.username,
        highest_score=1000,
        best_mean_hit_time=0.01,
        n_games=10,
        latest_game=TODAY,
    )
    user_score.merge(best_recent_score)
    assert user_score.highest_score == best_recent_score.highest_score
    assert user_score.n_games == init_n_game + best_recent_score.n_games
    assert user_score.latest_game == TODAY


def test_pretty_dict(user_score):
    assert user_score.pretty_dict() == {
        "best mean hit time": 0.1,
        "highest score": 100,
        "latest game": str(user_score.latest_game)[:10],
        "n games": 5,
        "username": "garbage1",
    }

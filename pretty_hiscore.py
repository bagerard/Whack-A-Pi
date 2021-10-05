import os

from scores import ScoreRepository
from beautifultable import BeautifulTable

score_file = os.environ.get("SCORE_FILE", "../../scores.json")

if not os.path.isfile(score_file):
    raise Exception(f"No Score file available: {score_file}")

JEDI_RANKS = [
    "Grand Master",
    "Master of the Order",
    "Jedi Council Member",
    "Jedi Master",
    "Jedi Sentinel",
    "Jedi Guardian",
    "Jedi Battlemaster",
    "Jedi Consular",
    "Jedi Knight",
    "Jedi Service Corps",
    "Padawan",
    "Youngling",
]

score_repo = ScoreRepository(filepath=score_file, backup_files=False)

ranked_hiscores = score_repo.ranked_user_scores

ranked_score = sorted({us.highest_score for us in ranked_hiscores}, reverse=1)
ranked_score_map = {score: rank for rank, score in enumerate(ranked_score, start=1)}

table = BeautifulTable(default_padding=2)
table.columns.header = ["Rank", "Jedi Rank", "User", "HiScore"]
for user_score in ranked_hiscores:
    user_rank = ranked_score_map[user_score.highest_score]
    jedi_rank = (
        JEDI_RANKS[user_rank - 1] if user_rank < len(JEDI_RANKS) else JEDI_RANKS[-1]
    )
    table.rows.append(
        [
            f"#{user_rank}",
            jedi_rank,
            user_score.username,
            f"{user_score.highest_score} points",
        ]
    )

print("                              - HiScores Table -")
print("")

print(table)

quotes = [
    (
        "“Once you start down the dark path, forever will it dominate your destiny.”",
        "Yoda, The Empire Strikes Back",
    ),
    ("“Uuuuuuuuuuur Ahhhhrrr Uhrrr Ahhhhhhrrr Aaaaarhg.....”", "Chewbacca"),
]

print("\n\n\n\n")
for quote, author in quotes:
    print(
        f"""
{quote}
                                        — {author}
    """
    )
    print("\n\n")

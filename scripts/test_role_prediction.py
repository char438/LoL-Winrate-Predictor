"""
One-off evaluation of the baseline role predictor.

Runs the champion-prior + Hungarian predictor over a set of matches and
compares predicted roles against the actual `position` stored in the DB.

Reports:
  - per-player accuracy   (of all players, what fraction got the right role)
  - per-team accuracy      (fraction of teams where all 5 were correct)
  - a confusion breakdown  (which actual roles get predicted as what)

This is analysis, not production: it imports the predictor and measures it.
"""

import sys
from collections import defaultdict
from dotenv import load_dotenv

# Adjust this import to wherever your predictor lives. If you run this from the
# project root, `src` needs to be importable; simplest is to run with
#   PYTHONPATH=src python scripts/eval_role_predictor.py
from role_predictor import predict_role
from db import get_connection

ROLES = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]


def get_test_match_ids(conn, limit=None):
    """Pull match ids to evaluate on. limit=None means all of them."""
    with conn.cursor() as cur:
        if limit is None:
            cur.execute("SELECT match_id FROM matches;")
        else:
            cur.execute("SELECT match_id FROM matches LIMIT %s;", (limit,))
        return [row[0] for row in cur.fetchall()]


def score_team(assignment, team):
    """
    Compare one team's predicted assignment against actual positions.

    assignment: {puuid: predicted_role}
    team:       list of player dicts, each with 'puuid' and 'position'

    Returns (correct_count, total_count, pairs) where pairs is a list of
    (actual_role, predicted_role) for the confusion breakdown.
    """
    correct = 0
    pairs = []
    for player in team:
        actual = player["position"]
        predicted = assignment[player["puuid"]]
        pairs.append((actual, predicted))
        if actual == predicted:
            correct += 1
    return correct, len(team), pairs


def main():
    load_dotenv()

    # Optional command-line limit: `python eval_role_predictor.py 200`
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    # Tallies
    player_correct = 0
    player_total = 0
    team_perfect = 0
    team_total = 0
    matches_evaluated = 0
    matches_skipped = 0

    # confusion[actual][predicted] = count
    confusion = defaultdict(lambda: defaultdict(int))

    with get_connection() as conn:
        match_ids = get_test_match_ids(conn, limit)
        print(f"Evaluating on {len(match_ids)} matches...\n")

        for match_id in match_ids:
            try:
                team_data, blue_assignment, red_assignment = predict_role(conn, match_id)
            except Exception as e:
                # Malformed match (not 5/5, missing champion in priors, etc.)
                # Skip it rather than crash the whole run.
                matches_skipped += 1
                continue

            matches_evaluated += 1

            for assignment, colour in (
                (blue_assignment, "blue"),
                (red_assignment, "red"),
            ):
                team = team_data[colour]
                correct, total, pairs = score_team(assignment, team)

                player_correct += correct
                player_total += total

                team_total += 1
                if correct == total:
                    team_perfect += 1

                for actual, predicted in pairs:
                    confusion[actual][predicted] += 1

    # ---- Report ----
    print("=" * 50)
    print(f"Matches evaluated: {matches_evaluated}")
    print(f"Matches skipped:   {matches_skipped}")
    print("-" * 50)

    if player_total:
        print(
            f"Per-player accuracy: {player_correct}/{player_total} "
            f"= {player_correct / player_total:.1%}"
        )
    if team_total:
        print(
            f"Per-team accuracy:   {team_perfect}/{team_total} "
            f"= {team_perfect / team_total:.1%}  (all 5 correct)"
        )

    # ---- Confusion breakdown ----
    print("-" * 50)
    print("Confusion (rows = actual, cols = predicted):\n")

    header = "actual \\ pred".ljust(14) + "".join(r[:4].rjust(8) for r in ROLES)
    print(header)
    for actual in ROLES:
        row = actual.ljust(14)
        for predicted in ROLES:
            row += str(confusion[actual][predicted]).rjust(8)
        print(row)

    print("=" * 50)


if __name__ == "__main__":
    main()
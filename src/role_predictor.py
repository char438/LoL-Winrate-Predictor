from db import role_predictor_bundle, get_connection
import numpy as np
from scipy.optimize import linear_sum_assignment

ROLES = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

def predict_role(conn, match_id):
    team_data, priors_lookup, spell_priors_lookup = role_predictor_bundle(conn, match_id)

    blue_matrix = -build_matrix(team_data["blue"], priors_lookup, spell_priors_lookup)
    red_matrix  = -build_matrix(team_data["red"],  priors_lookup, spell_priors_lookup)

    blue_assignment = cost_matrix_to_role_matching(blue_matrix, team_data["blue"])
    red_assignment  = cost_matrix_to_role_matching(red_matrix,  team_data["red"])

    return team_data, blue_assignment, red_assignment



def build_matrix(team_data, priors_lookup, spell_priors_lookup):
    matrix = []
    for player in team_data:
        player_probabilities = build_player_role_probabilities(
            player, priors_lookup, spell_priors_lookup
        )
        matrix.append(player_probabilities)

    return np.array(matrix, dtype=float)

def build_player_role_probabilities(player, priors_lookup, spell_priors_lookup):
    champ = player["champion_id"]

    combined_probabilities = []
    for role in ROLES:
        combined_probabilities.append(priors_lookup[champ][role])

    for spell_id in player["spell_ids"]:
        for role_index in range(len(ROLES)):
            role = ROLES[role_index]
            combined_probabilities[role_index] *= spell_priors_lookup[spell_id][role]

    total = sum(combined_probabilities)
    normalised_probabilities = []
    for probability in combined_probabilities:
        normalised_probabilities.append(probability / total)

    return normalised_probabilities


def cost_matrix_to_role_matching(cost_matrix, team):
    row_idx, col_idx = linear_sum_assignment(cost_matrix)
    assignment = {}
    for i, role_index in zip(row_idx, col_idx):
        player = team[i]
        assignment[player["puuid"]] = ROLES[role_index]
    return assignment



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    with get_connection() as conn:
        predict_role(conn, "OC1_665402940")
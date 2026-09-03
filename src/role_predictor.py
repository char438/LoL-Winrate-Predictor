from db import role_predictor_bundle, get_connection
import numpy as np
from scipy.optimize import linear_sum_assignment

ROLES = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

def predict_role(conn, match_id):
    team_data, priors_lookup = role_predictor_bundle(conn, match_id)

    blue_matrix = -build_matrix(team_data["blue"], priors_lookup)
    red_matrix  = -build_matrix(team_data["red"],  priors_lookup)

    blue_assignment = cost_matrix_to_role_matching(blue_matrix, team_data["blue"])
    red_assignment  = cost_matrix_to_role_matching(red_matrix,  team_data["red"])

    return team_data, blue_assignment, red_assignment


def build_matrix(team_data, priors_lookup):
    matrix = []

    for player in team_data:
        champ = player["champion_id"]
        row = [priors_lookup[champ][role] for role in ROLES] 
        matrix.append(row)

    return np.array(matrix, dtype=float)


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
    predict_role("OC1_665402940")
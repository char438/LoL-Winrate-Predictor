import os, psycopg
from psycopg.types.json import Json


def get_connection():
    return psycopg.connect(os.getenv("DATABASE_URL"))

def insert_data_pipeline(conn, match_json, match_row, participant_rows, ban_rows):
    insert_raw_match(conn, match_row["match_id"], match_json)
    insert_match(conn, match_row)
    insert_players(conn, participant_rows)
    insert_participants(conn, participant_rows)
    insert_bans(conn, ban_rows)
    mark_processed(conn, match_row["match_id"])

def insert_raw_match(conn, match_id, match_json):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO raw_matches (match_id, raw_json) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (match_id, Json(match_json)),
        )

def insert_match(conn, match_row):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO matches (match_id, patch, start_time, winner_side, game_duration)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT DO NOTHING""",
            (match_row["match_id"], match_row["patch"], match_row["start_time"],
             match_row["winner_side"], match_row["game_duration"]),
        )

def insert_players(conn, participant_rows):
    puuids = {p["puuid"] for p in participant_rows} 
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO players (puuid) VALUES (%s) ON CONFLICT DO NOTHING",
            [(puuid,) for puuid in puuids],
        )


def insert_participants(conn, participant_rows):
    with conn.cursor() as cur:
        cur.executemany(
            """INSERT INTO participants
               (match_id, puuid, team_colour, champion_id, champion_name,
                summoner1_id, summoner2_id, keystone_id, primary_style,
                secondary_style, position)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT DO NOTHING""",
            [(p["match_id"], p["puuid"], p["team_colour"], p["champion_id"],
              p["champion_name"], p["summoner1_id"], p["summoner2_id"],
              p["keystone_id"], p["primary_style"], p["secondary_style"],
              p["position"]) for p in participant_rows],
        )


def insert_bans(conn, ban_rows):
    with conn.cursor() as cur:
        cur.executemany(
            """INSERT INTO bans (match_id, team_colour, champion_id, pick_turn)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT DO NOTHING""",
            [(b["match_id"], b["team_colour"], b["champion_id"], b["pick_turn"])
             for b in ban_rows],
        )

def update_player_rank(conn, player_row):
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE players
               SET tier = %s, division = %s, lp = %s
               WHERE puuid = %s""",
            (player_row["tier"], player_row["division"],
             player_row["lp"], player_row["puuid"]),
        )

def matchid_already_processed(conn, match_id):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM processed_matches WHERE match_id = %s", (match_id,))
        return cur.fetchone() is not None

def mark_processed(conn, match_id):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO processed_matches (match_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (match_id,),
        )


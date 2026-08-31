from datetime import datetime, timezone


def _team_colour(team_id):
    return "blue" if team_id == 100 else "red"


def _patch(game_version):
    return ".".join(game_version.split(".")[:2])  # "14.16.632.9139" -> "14.16"


def parse_match_json(match_json):
    info = match_json["info"]
    match_id = match_json["metadata"]["matchId"]

    # --- match row (one dict) ---
    winner_side = next(_team_colour(t["teamId"]) for t in info["teams"] if t["win"])
    match_row = {
        "match_id": match_id,
        "patch": _patch(info["gameVersion"]),
        "start_time": datetime.fromtimestamp(info["gameStartTimestamp"] / 1000, tz=timezone.utc),
        "winner_side": winner_side,
    }

    # --- participant rows (ten dicts) ---
    participant_rows = []
    for p in info["participants"]:
        styles = p["perks"]["styles"]
        participant_rows.append({
            "match_id": match_id,
            "puuid": p["puuid"],
            "team_colour": _team_colour(p["teamId"]),
            "champion_id": p["championId"],
            "champion_name": p["championName"],
            "summoner1_id": p["summoner1Id"],
            "summoner2_id": p["summoner2Id"],
            "keystone_id": styles[0]["selections"][0]["perk"],
            "primary_style": styles[0]["style"],
            "secondary_style": styles[1]["style"],
            "position": p["teamPosition"],
        })

    # --- ban rows (varies) ---
    ban_rows = []
    for t in info["teams"]:
        colour = _team_colour(t["teamId"])
        for b in t["bans"]:
            if b["championId"] == -1:   # empty ban slot
                continue
            ban_rows.append({
                "match_id": match_id,
                "team_colour": colour,
                "champion_id": b["championId"],
                "pick_turn": b["pickTurn"],
            })

    return match_row, participant_rows, ban_rows



if __name__ == "__main__":
    from riot_client import get_puuid_by_riot_id, get_matchlist_by_puuid, get_match_by_match_id

    puuid = get_puuid_by_riot_id("tenpaireformed", "oc", "asia")
    match_id = get_matchlist_by_puuid("sea", puuid)[0]
    match_json = get_match_by_match_id("sea", match_id)

    match_row, participant_rows, ban_rows = parse_match_json(match_json)
    print(match_row)
    print(participant_rows[0])   # just the first player
    print(ban_rows)

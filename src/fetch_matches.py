from collections import deque
import time
from riot_client import get_matchlist_by_puuid, get_match_by_match_id
from parse import parse_match_json
from db import insert_data_pipeline, matchid_already_processed, get_connection, mark_processed


def crawl(seed_puuid, region, target_matches):
    queue = deque([seed_puuid])
    seen_players = {seed_puuid}
    processed_matches_cache = set()
    stored = 0

    with get_connection() as conn:
        while queue and stored < target_matches:
            current_puuid = queue.popleft()
            current_matchlist = get_matchlist_by_puuid(region, current_puuid)

            for matchid in current_matchlist:
                if matchid in processed_matches_cache:
                    continue
                if matchid_already_processed(conn, matchid):
                    continue

                try:
                    current_match_json = get_match_by_match_id(region, matchid)

                    if current_match_json["info"]["queueId"] != 420:
                        processed_matches_cache.add(matchid)
                        mark_processed(conn, matchid)
                        conn.commit()
                    else:
                        current_team_list = current_match_json["metadata"]["participants"]
                        for puuid in current_team_list:
                            if puuid not in seen_players:
                                queue.append(puuid)
                                seen_players.add(puuid)

                        match_row, participant_rows, ban_rows = parse_match_json(current_match_json)
                        insert_data_pipeline(conn, match_row, participant_rows, ban_rows)
                        conn.commit()
                        processed_matches_cache.add(matchid)   # #6
                        stored += 1
                        print(f"stored {stored}: {matchid}")

                    time.sleep(1.2)   # rate limit, after each match fetch

                except Exception as e:
                    conn.rollback()
                    print(f"Skipping {matchid}: {e}")
                    continue

if __name__ == "__main__":
    from dotenv import load_dotenv
    from riot_client import get_puuid_by_riot_id
    load_dotenv()

    seed = get_puuid_by_riot_id("tenpaireformed", "oc", "asia")
    crawl(seed, "sea", target_matches=5) 
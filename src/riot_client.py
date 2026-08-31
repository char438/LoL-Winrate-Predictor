import requests
import os
from dotenv import load_dotenv

load_dotenv()
riot_key = os.getenv("RIOT_API_KEY")


def _riot_get(url):
    headers = {"X-Riot-Token": riot_key}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() 
    return response.json()


def get_puuid_by_riot_id(game_name, tag_line, region):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    return _riot_get(url)["puuid"] 


def get_matchlist_by_puuid(region, puuid):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    return _riot_get(url)


def get_match_by_match_id(region, matchId):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{matchId}"
    return _riot_get(url)

def get_player_info_by_puuid(region, puuid):
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    return _riot_get(url)



if __name__ == "__main__":
    puuid = get_puuid_by_riot_id("tenpaireformed", "oc", "asia")
    matchlist = get_matchlist_by_puuid("sea", puuid)
    match_data = get_match_by_match_id("sea", matchlist[0])

    


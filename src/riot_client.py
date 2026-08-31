import requests
import os
from dotenv import load_dotenv

load_dotenv()
riot_key = os.getenv("RIOT_API_KEY")


def get_uuid_by_riot(gameName, tagLine, region, api_key):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    headers = {
        "X-Riot-Token": api_key
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data['puuid']  # This is the UUID of the summoner
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None




uuid = get_uuid_by_riot("tenpaireformed", "oc", "asia", riot_key)


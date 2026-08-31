matches:
  match_id      text  pk                  -- Riot ids look like "OC1_123456789"
  patch         text                      -- from gameVersion, first two parts
  start_time    timestamptz               -- Riot gives epoch ms (bigint); convert on insert
  winner_side   text                      -- 'blue' / 'red'

participants:
  match_id      text  references matches(match_id)
  puuid         text  references players(puuid)
  primary key (match_id, puuid)           -- composite: one row per player per match
  team_colour   text                      -- 'blue' / 'red' (match winner_side values)
  champion_id   int                       -- stable key; canonical
  champion_name text                      -- optional, readability only
  summoner1_id  int
  summoner2_id  int
  keystone_id   int                       -- from perks
  primary_style int
  secondary_style int
  position      text                      -- teamPosition: TOP/JUNGLE/MIDDLE/BOTTOM/UTILITY

players:
  puuid          text  pk
  tier           text                     -- nullable; filled by league-v4 later
  division       text                     -- nullable
  lp             int                      -- nullable
  summoner_level int                      -- optional

bans:                                     -- optional / low priority
  match_id      text  references matches(match_id)
  team_colour   text
  champion_id   int
  pick_turn     int
  primary key (match_id, champion_id)


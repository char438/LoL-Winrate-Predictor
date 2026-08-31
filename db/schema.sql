CREATE TABLE players (
    puuid          text primary key,
    tier           text,
    division       text,
    lp             int,
    summoner_level int
);

CREATE TABLE matches (
    match_id       text primary key,
    patch          text,
    start_time     timestamptz,
    winner_side    text,
    game_duration  int
);

CREATE TABLE participants (
    match_id        text references matches(match_id),
    puuid           text references players(puuid),
    team_colour     text,
    champion_id     int,
    champion_name   text,
    summoner1_id    int,
    summoner2_id    int,
    keystone_id     int,
    primary_style   int,
    secondary_style int,
    position        text,
    primary key (match_id, puuid)
);

CREATE TABLE bans (
    match_id     text references matches(match_id),
    team_colour  text,
    champion_id  int,
    pick_turn    int,
    primary key (match_id, champion_id)
);

CREATE TABLE processed_matches (
    match_id text primary key
);

CREATE TABLE raw_matches (
    match_id text primary key,
    raw_json jsonb
);
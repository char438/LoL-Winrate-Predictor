DROP TABLE IF EXISTS role_priors;

CREATE TABLE role_priors AS
with role_counts as (
    select champion_name, champion_id, position, count(*) as games_played
    from participants
    where position is not null and position <> ''
    group by champion_name, champion_id, position
),
all_champions as (
    select distinct champion_name, champion_id from role_counts
),
all_roles as (
    select unnest(array['TOP','JUNGLE','MIDDLE','BOTTOM','UTILITY']) as position
),
grid as (
    select c.champion_name, c.champion_id, r.position
    from all_champions c
    cross join all_roles r
)
select
    g.champion_name,
    g.champion_id,
    g.position,
    coalesce(rc.games_played, 0) as games_played,
    sum(coalesce(rc.games_played, 0)) over (partition by g.champion_name) as total_champion_games,
    (coalesce(rc.games_played, 0) + 1)::numeric
        / (sum(coalesce(rc.games_played, 0)) over (partition by g.champion_name) + 5) -- laplace smoothing with alpha = 1
        as champion_role_pickrate
from grid g
left join role_counts rc
    on g.champion_name = rc.champion_name
    and g.position = rc.position;
DROP TABLE IF EXISTS spell_role_priors;
CREATE TABLE spell_role_priors AS
with spell_plays as (
    -- one row per (spell, role) occurrence, folding both spell slots together
    select summoner1_id as spell_id, position from participants
    where position is not null and position <> ''
    union all
    select summoner2_id as spell_id, position from participants
    where position is not null and position <> ''
),
spell_counts as (
    select spell_id, position, count(*) as games_played
    from spell_plays
    group by spell_id, position
),
all_spells as (
    select distinct spell_id from spell_counts
),
all_roles as (
    select unnest(array['TOP','JUNGLE','MIDDLE','BOTTOM','UTILITY']) as position
),
grid as (
    select s.spell_id, r.position
    from all_spells s
    cross join all_roles r
)
select
    g.spell_id,
    g.position,
    coalesce(sc.games_played, 0) as games_played,
    (coalesce(sc.games_played, 0) + 1)::numeric
        / (sum(coalesce(sc.games_played, 0)) over (partition by g.spell_id) + 5)
        as spell_role_pickrate
from grid g
left join spell_counts sc
    on g.spell_id = sc.spell_id
    and g.position = sc.position;
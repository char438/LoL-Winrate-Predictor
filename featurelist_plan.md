red top vs blue top relative strength this patch (depends how we store the relative strength how we store this one)
(and also for mid, jg, adc, sup)

red top vs blue top rank difference (and the same for other roles)

red top vs blue top last n games winrate (as above)

(perhaps for some of these lane based features, we should be considering adc + supp as a combo as well as by themselves?)

per user champion mastery scores for the certain champion they are playing

per user champion similarity playrate scores (i.e. do they tend to play mages or not, maybe over the last n games how many matches of that type have they played, as well as champion masteries on class type)

per user role similarity (similarly to above but we map champions into lanes instead of classes) -> need to clarify if the live match api pulls their locked in role at champ select, if it does then we can use, if not maybe we can make estimates









Per-player, history-derived (the recipe: point-in-time → aggregate → shrink → count → optional recency)
Overall recent form (win rate over prior games)
Champion win rate (on the champ they're playing this game)
Champion-matchup win rate (their champ vs lane opponent's champ) — sparse, aggregates poorly, wants lane-pairing
Role/position experience (games on the role they're playing) — needs live role inference
Same-class experience (games on champs of the same class: tank/bruiser/enchanter etc.) — needs Data Dragon champ→class mapping
Per-player, cheap lookups (not history-derived)
Rank (tier / division / LP) — 1 league-v4 call each; point-in-time-unsafe for training
Champion mastery (points/level on played champ) — 1 champion-mastery-v4 call each; also point-in-time-unsafe for training
Champion-level (not player-level)
Champion strength per patch (global win rate of the champ on this patch) — patch-relative, most drift-exposed
Match-level / structural (nearly free)
Side (blue/red flag)
Patch (control, not really a standalone predictor)
Future work (parked, don't build early)
Teammate synergy (win rate playing with specific teammates)
Opponent history (win rate against specific opponents)
Side-dependent player skill (a player's win rate specifically on blue vs red side)
Cross-cutting things that aren't features but shape them
Team aggregation (how 10 players collapse to team numbers: mean / min / max / variance / difference) — per-feature, not global
Rank-gap (blue team rank vs red team rank) — a derived team-level feature once rank is aggregated
Sample-size count columns (paired with every shrunk rate)
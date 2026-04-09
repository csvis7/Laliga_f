from pathlib import Path
import pandas as pd
from understatapi import UnderstatClient


SEASON_YEAR = "2025"
SEASON_CODE = 2026
LEAGUE_NAME = "La_Liga"

REPO_ROOT = Path(__file__).resolve().parents[1]
MATCHES_OUTPUT = REPO_ROOT / "MatchPredicting" / "matches.csv"
PLAYER_OUTPUT = REPO_ROOT / "prem_stats.csv"

MATCH_COLUMNS = [
    "date", "time", "comp", "round", "day", "venue", "result", "gf", "ga", "opponent",
    "xg", "xga", "poss", "attendance", "captain", "formation", "referee",
    "match report", "notes", "sh", "sot", "dist", "fk", "pk", "pkatt", "season", "team"
]

PLAYER_COLUMNS = [
    "Player", "Nation", "Pos", "Age", "MP", "Starts", "Min", "Gls", "Ast", "PK",
    "CrdY", "CrdR", "xG", "xAG", "Team"
]


def match_result(gf: int, ga: int) -> str:
    if gf > ga:
        return "W"
    if gf < ga:
        return "L"
    return "D"


def scrape_laliga_2025_26() -> tuple[pd.DataFrame, pd.DataFrame]:
    understat = UnderstatClient()
    league = understat.league(league=LEAGUE_NAME)
    matches_raw = league.get_match_data(season=SEASON_YEAR)
    players_raw = league.get_player_data(season=SEASON_YEAR)

    # Build one row per team per match, aligned with existing matches.csv structure.
    match_rows = []
    for m in matches_raw:
        if not m.get("isResult"):
            continue
        dt = pd.to_datetime(m["datetime"])
        home_team = m["h"]["title"]
        away_team = m["a"]["title"]
        home_goals = int(m["goals"]["h"])
        away_goals = int(m["goals"]["a"])
        home_xg = float(m["xG"]["h"])
        away_xg = float(m["xG"]["a"])

        base = {
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M"),
            "comp": "La Liga",
            "round": pd.NA,
            "day": dt.strftime("%a"),
            "match report": "Match Report",
            "notes": pd.NA,
            "poss": pd.NA,
            "attendance": pd.NA,
            "captain": pd.NA,
            "formation": pd.NA,
            "referee": pd.NA,
            "sh": pd.NA,
            "sot": pd.NA,
            "dist": pd.NA,
            "fk": pd.NA,
            "pk": pd.NA,
            "pkatt": pd.NA,
            "season": SEASON_CODE,
        }

        match_rows.append({
            **base,
            "venue": "Home",
            "team": home_team,
            "opponent": away_team,
            "gf": home_goals,
            "ga": away_goals,
            "xg": home_xg,
            "xga": away_xg,
            "result": match_result(home_goals, away_goals),
        })
        match_rows.append({
            **base,
            "venue": "Away",
            "team": away_team,
            "opponent": home_team,
            "gf": away_goals,
            "ga": home_goals,
            "xg": away_xg,
            "xga": home_xg,
            "result": match_result(away_goals, home_goals),
        })

    matches_df = pd.DataFrame(match_rows)[MATCH_COLUMNS]
    matches_df = matches_df.sort_values(by=["date", "team"]).reset_index(drop=True)

    # Build player stats in same column layout as existing prem_stats.csv.
    player_rows = []
    for p in players_raw:
        player_rows.append({
            "Player": p.get("player_name"),
            "Nation": pd.NA,
            "Pos": p.get("position"),
            "Age": pd.NA,
            "MP": pd.to_numeric(p.get("games"), errors="coerce"),
            "Starts": pd.NA,
            "Min": pd.to_numeric(p.get("time"), errors="coerce"),
            "Gls": pd.to_numeric(p.get("goals"), errors="coerce"),
            "Ast": pd.to_numeric(p.get("assists"), errors="coerce"),
            "PK": pd.to_numeric(p.get("goals"), errors="coerce") - pd.to_numeric(p.get("npg"), errors="coerce"),
            "CrdY": pd.to_numeric(p.get("yellow_cards"), errors="coerce"),
            "CrdR": pd.to_numeric(p.get("red_cards"), errors="coerce"),
            "xG": pd.to_numeric(p.get("xG"), errors="coerce"),
            "xAG": pd.to_numeric(p.get("xA"), errors="coerce"),
            "Team": p.get("team_title"),
        })

    players_df = pd.DataFrame(player_rows)[PLAYER_COLUMNS]
    players_df = players_df.sort_values(by=["Team", "Player"]).reset_index(drop=True)
    return matches_df, players_df


if __name__ == "__main__":
    matches_df, players_df = scrape_laliga_2025_26()
    matches_df.to_csv(MATCHES_OUTPUT)
    players_df.to_csv(PLAYER_OUTPUT, index=False)
    print(f"Saved {len(matches_df)} rows to {MATCHES_OUTPUT}")
    print(f"Saved {len(players_df)} rows to {PLAYER_OUTPUT}")

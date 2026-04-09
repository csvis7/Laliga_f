from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from understatapi import UnderstatClient


DATA_PATH = Path(__file__).resolve().parent / "matches.csv"
FUTURE_OUTPUT_PATH = Path(__file__).resolve().parent / "future_predictions.csv"
SEASON_YEAR = "2025"  # Understat season key for 2025/26


def rolling_averages(group: pd.DataFrame, cols: list[str], new_cols: list[str]) -> pd.DataFrame:
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left").mean()
    group[new_cols] = rolling_stats
    return group.dropna(subset=new_cols)


def load_and_prepare_matches() -> tuple[pd.DataFrame, list[str], dict[str, int]]:
    matches = pd.read_csv(DATA_PATH, index_col=0)
    matches["date"] = pd.to_datetime(matches["date"])
    matches["hour"] = pd.to_numeric(matches["time"].astype(str).str.extract(r"^(\d{1,2})")[0], errors="coerce")
    matches["day"] = matches["date"].dt.dayofweek
    matches["target"] = (matches["result"] == "W").astype(int)
    matches["h/a"] = matches["venue"].map({"Home": 1, "Away": 0}).fillna(0).astype(int)

    opponent_codes = {team: i for i, team in enumerate(sorted(matches["opponent"].dropna().unique()))}
    matches["opp"] = matches["opponent"].map(opponent_codes).fillna(-1).astype(int)

    rolling_cols = [c for c in ["gf", "ga", "xg", "xga", "sh", "sot", "dist", "fk", "pk", "pkatt"] if c in matches.columns and matches[c].notna().any()]
    if len(rolling_cols) < 2:
        rolling_cols = ["gf", "ga"]
    new_cols = [f"{c}_rolling" for c in rolling_cols]

    matches_rolling = pd.concat(
        [rolling_averages(group, rolling_cols, new_cols) for _, group in matches.groupby("team")],
        ignore_index=True,
    )
    return matches_rolling, new_cols, opponent_codes


def train_model(data: pd.DataFrame, predictors: list[str]) -> tuple[RandomForestClassifier, float]:
    rf = RandomForestClassifier(n_estimators=200, min_samples_split=10, random_state=1)
    split_date = data["date"].quantile(0.7)
    train = data[data["date"] <= split_date]
    test = data[data["date"] > split_date]

    rf.fit(train[predictors], train["target"])
    preds = rf.predict(test[predictors])
    precision = precision_score(test["target"], preds, zero_division=0)
    return rf, precision


def last_team_form(data: pd.DataFrame, team: str, rolling_feature_names: list[str]) -> dict[str, float]:
    team_rows = data[data["team"] == team].sort_values("date")
    if team_rows.empty:
        return {c: 0.0 for c in rolling_feature_names}
    latest = team_rows.iloc[-1]
    return {c: float(latest.get(c, 0.0) or 0.0) for c in rolling_feature_names}


def fetch_future_fixtures() -> list[dict]:
    understat = UnderstatClient()
    match_data = understat.league("La_Liga").get_match_data(SEASON_YEAR)
    return [m for m in match_data if not m.get("isResult")]


def predict_future_matches(
    rf: RandomForestClassifier,
    prepared_data: pd.DataFrame,
    predictors: list[str],
    rolling_features: list[str],
    opponent_codes: dict[str, int],
) -> pd.DataFrame:
    future_matches = fetch_future_fixtures()
    rows = []

    for fixture in future_matches:
        dt = pd.to_datetime(fixture["datetime"])
        home_team = fixture["h"]["title"]
        away_team = fixture["a"]["title"]
        hour = int(dt.hour)
        day = int(dt.dayofweek)

        home_form = last_team_form(prepared_data, home_team, rolling_features)
        away_form = last_team_form(prepared_data, away_team, rolling_features)

        home_input = {"h/a": 1, "opp": opponent_codes.get(away_team, -1), "hour": hour, "day": day, **home_form}
        away_input = {"h/a": 0, "opp": opponent_codes.get(home_team, -1), "hour": hour, "day": day, **away_form}

        home_df = pd.DataFrame([home_input])[predictors]
        away_df = pd.DataFrame([away_input])[predictors]

        home_win_prob = float(rf.predict_proba(home_df)[0][1])
        away_win_prob = float(rf.predict_proba(away_df)[0][1])

        if abs(home_win_prob - away_win_prob) < 0.08:
            prediction = "Draw"
        elif home_win_prob > away_win_prob:
            prediction = "Home Win"
        else:
            prediction = "Away Win"

        rows.append(
            {
                "date": dt.date().isoformat(),
                "time": dt.strftime("%H:%M"),
                "home_team": home_team,
                "away_team": away_team,
                "home_win_prob": round(home_win_prob, 4),
                "away_win_prob": round(away_win_prob, 4),
                "prediction": prediction,
            }
        )

    future_df = pd.DataFrame(rows).sort_values(["date", "time", "home_team"]).reset_index(drop=True)
    future_df.to_csv(FUTURE_OUTPUT_PATH, index=False)
    return future_df


if __name__ == "__main__":
    matches_rolling, rolling_features, opponent_codes = load_and_prepare_matches()
    base_predictors = ["h/a", "opp", "hour", "day"]
    all_predictors = base_predictors + rolling_features

    model, precision = train_model(matches_rolling, all_predictors)
    future_predictions = predict_future_matches(
        model,
        matches_rolling,
        all_predictors,
        rolling_features,
        opponent_codes,
    )

    print(f"Model precision on holdout set: {precision:.4f}")
    print(f"Future fixtures predicted: {len(future_predictions)}")
    print(f"Saved to: {FUTURE_OUTPUT_PATH}")
    if not future_predictions.empty:
        print("\nNext 15 predictions:")
        print(future_predictions.head(15).to_string(index=False))

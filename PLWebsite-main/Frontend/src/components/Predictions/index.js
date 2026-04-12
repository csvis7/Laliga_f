import { useEffect, useState } from "react";
import axios from "axios";
import AnimatedLetters from "../AnimatedLetters";
import "./index.scss";

const Predictions = () => {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get("https://laliga-f.onrender.com/api/v1/predictions")
      .then((response) => {
        setRows(response.data || []);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="container predictions-page">
      <h1 className="page-title">
        <AnimatedLetters
          letterClass="text-animate"
          strArray={"Predictions".split("")}
          idx={12}
        />
      </h1>

      {loading && <p>Loading predictions...</p>}
      {error && <p>Error: {error}</p>}

      {!loading && !error && (
        <div className="predictions-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Home</th>
                <th>Away</th>
                <th>Home Win Prob</th>
                <th>Away Win Prob</th>
                <th>Prediction</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, idx) => (
                <tr key={`${r.date}-${r.time}-${r.home_team}-${idx}`}>
                  <td>{r.date}</td>
                  <td>{r.time}</td>
                  <td>{r.home_team}</td>
                  <td>{r.away_team}</td>
                  <td>{r.home_win_prob}</td>
                  <td>{r.away_win_prob}</td>
                  <td>{r.prediction}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Predictions;

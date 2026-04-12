package com.example.pl_connect.prediction;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.LocalTime;

@Entity
@Table(name = "predictions")
public class Prediction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private LocalDate date;
    private LocalTime time;
    private String home_team;
    private String away_team;
    private Double home_win_prob;
    private Double away_win_prob;
    private String prediction;

    // Getters and Setters
    public Long getId() { return id; }
    public LocalDate getDate() { return date; }
    public LocalTime getTime() { return time; }
    public String getHome_team() { return home_team; }
    public String getAway_team() { return away_team; }
    public Double getHome_win_prob() { return home_win_prob; }
    public Double getAway_win_prob() { return away_win_prob; }
    public String getPrediction() { return prediction; }
    public void setId(Long id) { this.id = id; }
    public void setDate(LocalDate date) { this.date = date; }
    public void setTime(LocalTime time) { this.time = time; }
    public void setHome_team(String home_team) { this.home_team = home_team; }
    public void setAway_team(String away_team) { this.away_team = away_team; }
    public void setHome_win_prob(Double home_win_prob) { this.home_win_prob = home_win_prob; }
    public void setAway_win_prob(Double away_win_prob) { this.away_win_prob = away_win_prob; }
    public void setPrediction(String prediction) { this.prediction = prediction; }
}
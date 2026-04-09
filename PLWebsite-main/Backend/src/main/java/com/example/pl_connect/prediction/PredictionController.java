package com.example.pl_connect.prediction;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping(path = "api/v1/predictions")
public class PredictionController {

    private Path resolvePredictionsFile() {
        Path[] candidates = new Path[]{
                Path.of("MatchPredicting", "future_predictions.csv"),
                Path.of("..", "MatchPredicting", "future_predictions.csv"),
                Path.of("PLWebsite-main", "MatchPredicting", "future_predictions.csv"),
                Path.of("..", "PLWebsite-main", "MatchPredicting", "future_predictions.csv")
        };

        for (Path candidate : candidates) {
            Path normalized = candidate.toAbsolutePath().normalize();
            if (Files.exists(normalized)) {
                return normalized;
            }
        }
        return null;
    }

    @GetMapping
    public List<Map<String, String>> getPredictions() throws IOException {
        Path filePath = resolvePredictionsFile();
        if (filePath == null) {
            return List.of();
        }

        List<String> lines = Files.readAllLines(filePath);
        if (lines.isEmpty()) {
            return List.of();
        }

        String[] headers = lines.get(0).split(",", -1);
        List<Map<String, String>> result = new ArrayList<>();

        for (int i = 1; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.isBlank()) {
                continue;
            }
            String[] values = line.split(",", -1);
            Map<String, String> row = new LinkedHashMap<>();
            for (int j = 0; j < headers.length; j++) {
                String value = j < values.length ? values[j] : "";
                row.put(headers[j], value);
            }
            result.add(row);
        }

        return result;
    }
}

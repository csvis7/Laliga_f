package com.example.pl_connect.prediction;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping(path = "api/v1/predictions")
public class PredictionController {

    @Autowired
    private PredictionRepository predictionRepository;

    @GetMapping
    public List<Prediction> getPredictions() {
        return predictionRepository.findAll();
    }
}
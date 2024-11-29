-- SELECT experiment.experiment_id, experiment.subject_id, species.species_name, experiment.experiment_date, experiment_type.type_name, experiment.score FROM experiment
-- JOIN subject USING (subject_id)
-- JOIN species USING (species_id)
-- JOIN experiment_type USING(experiment_type_id)
-- ;

-- SELECT *
-- FROM experiment
-- JOIN subject USING (subject_id)
-- JOIN species USING (species_id)
-- JOIN experiment_type USING(experiment_type_id)
-- ORDER BY experiment.experiment_date DESC
-- ;



{
  "subject_id": 3,
  "experiment_type": "obedience",
  "experiment_date": "2024-03-01",
  "score": 7
}
```
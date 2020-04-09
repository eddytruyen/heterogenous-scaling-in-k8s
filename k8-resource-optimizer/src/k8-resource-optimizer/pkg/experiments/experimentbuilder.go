package experiments

import (
	"encoding/json"
	"log"

	"k8-resource-optimizer/pkg/models"
)

func ExperimentBuilder(experimentType string, slas []models.SLA, outputDir string) *models.Experiment {

	var experiment models.Experiment
	switch experimentType {
	case "locustBatchFromNamespaces":
		experiment = locustBatchFromNamespaces(slas)
		experiment.SetOutputDir(outputDir)
		break
	case "LocustRequestExperiment":
		experiment = createLocustRequestExperiment(slas)
		experiment.SetOutputDir(outputDir)
		break
	default:
		log.Fatalf("ExperimentBuilder: unable to create experiment of type %v", experimentType)
		panic("")
	}

	return &experiment

}

func ExperimentUnmarshalJSON(raw *json.RawMessage) (models.Experiment, error) {
	// deserialize into map
	var rawMap map[string]*json.RawMessage
	err := json.Unmarshal(*raw, &rawMap)
	if err != nil {
		log.Printf("ExperimentUnmarshalJSON error 0")
		return nil, err
	}

	var experimentType string
	err = json.Unmarshal(*rawMap["Type"], &experimentType)
	if err != nil {
		log.Printf("ExperimentUnmarshalJSON error 1")
		return nil, err

	}

	switch experimentType {
	case "LocustBatchExperiment":
		var value models.Experiment
		value = &LocustBatchExperiment{}
		err = json.Unmarshal(*raw, value)
		if err != nil {
			log.Printf("ExperimentUnmarshalJSON error 2")
			return nil, err
		}
		return value, nil
	}

	return nil, nil
}

func ResultUnmarshalJSON(raw *json.RawMessage) (models.ExperimentResult, error) {
	// deserialize into map
	var rawMap map[string]*json.RawMessage
	err := json.Unmarshal(*raw, &rawMap)
	if err != nil {
		log.Printf("ResultUnmarshalJSON error 0")
		return nil, err
	}
	var typeResult string
	err = json.Unmarshal(*rawMap["Type"], &typeResult)
	if err != nil {
		log.Printf("ResultUnmarshalJSON error 1")
		return nil, err

	}

	switch typeResult {
	case "LocustBatchExperimentResult":
		var value models.ExperimentResult
		value = &LocustBatchExperimentResult{}
		err = json.Unmarshal(*raw, value)
		if err != nil {
			log.Printf("ResultUnmarshalJSON error 2")
			return nil, err
		}
		return value, nil
	case "LocustBatchInnerExperimentResult":
		var value models.ExperimentResult
		value = &LocustBatchInnerExperimentResult{}
		err = json.Unmarshal(*raw, value)
		if err != nil {
			log.Printf("ResultUnmarshalJSON error 3")
			return nil, err
		}
		return value, nil
	}

	return nil, nil
}

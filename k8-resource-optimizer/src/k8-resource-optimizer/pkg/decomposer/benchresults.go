package decomposer

import (
	"encoding/json"
	"log"
	"os"

	"k8-resource-optimizer/pkg/experiments"
)

func (d *Decomposer) saveResultsJSON(path string) {
	data, err := json.Marshal(d.BenchResults)
	if err != nil {
		log.Fatalf("error: %v", err)
	}
	// err1 := os.Remove(c.tempDir + "/values.yaml")

	file, err2 := os.Create(path)
	if err2 != nil {
		log.Fatalf("Decomposer: could create benchResult file : %v", path)
	}
	file.Write(data)
	defer file.Close()
}

func (br *BenchResult) UnmarshalJSON(b []byte) error {
	// deserialize into map
	var objMap map[string]*json.RawMessage
	err := json.Unmarshal(b, &objMap)
	if err != nil {
		return err
	}

	//deserialize namespaces
	err = json.Unmarshal(*objMap["bench"], &br.Bench)
	if err != nil {
		return err
	}

	br.Result, err = experiments.ResultUnmarshalJSON(objMap["result"])
	if err != nil {
		return err
	}
	return nil
}

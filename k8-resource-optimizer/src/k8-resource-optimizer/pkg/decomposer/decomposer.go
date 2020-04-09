package decomposer

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"strings"

	"k8-resource-optimizer/pkg/utils"

	"k8-resource-optimizer/pkg/bench"
	"k8-resource-optimizer/pkg/experiments"
	"k8-resource-optimizer/pkg/models"
	"k8-resource-optimizer/pkg/optimizers"
	"k8-resource-optimizer/pkg/optimizers/utilityfunc"

	yaml "gopkg.in/yaml.v2"
)

type Decomposer struct {
	NbOfIterations          int            `yaml:"nbOfIterations"`
	NbOfSamplesPerIteration int            `yaml:"nbOfSamplesPerIteration"`
	Charts                  []models.Chart `yaml:"charts"`
	Slas                    []models.SLA   `yaml:"slas"`
	NamespaceStrategy       string         `yaml:"namespaceStrategy"`
	Optimizer               string         `yaml:"optimizer"`
	PrevResultsPath         string         `yaml:"prevResultsPath"`
	BenchResults            []BenchResult  `yaml:"results"`
	OutputDir               string         `yaml:"outputDir"`
	UtilFunc                string         `yaml:"utilFunc"`
	offline                 bool
}
type BenchResult struct {
	Bench  bench.Bench             `json:"bench"`
	Result models.ExperimentResult `json:"result"`
}

func (d *Decomposer) SetOutputDir(dir string) {
	if !strings.HasSuffix(dir, "/") {
		dir = dir + "/"
	}
	d.OutputDir = dir
}

func NewDecomposerFromFile(path string) (Decomposer, error) {
	d := Decomposer{}
	raw, err := ioutil.ReadFile(path)
	if err != nil {
		log.Printf("Decomposer: NewDecomposerFromFile: error reading decomposer config: %v", err.Error())
		return d, err
	}
	err = yaml.Unmarshal(raw, &d)
	if err != nil {
		log.Printf("Decomposer: NewDecomposerFromFile: Error executing yaml unmarshall: %v", err)
		return d, err
	}

	// if previous results file specified.
	if d.PrevResultsPath != "" {
		raw, err = ioutil.ReadFile(d.PrevResultsPath)
		if err != nil {
			log.Printf("Decomposer: NewDecomposerFromFile: Error reading of previous results: %v", err)
			return d, err
		}
		err = json.Unmarshal(raw, &d.BenchResults)
		if err != nil {
			log.Printf("Decomposer: NewDecomposerFromFile: Error executing json unmarshall of previous results: %v", err)
			return d, err
		}

		log.Printf("Decomposer loaded dataset containing %v previously executed benchmarks", len(d.BenchResults))
	}

	return d, nil
}

func (d *Decomposer) Execute(offline bool) {
	d.offline = offline
	// generate extra SLA if required for the Namespace strategy
	d.employNameSpaceStrategy()
	// create the selected optimizer
	optimizers := d.initializeOptimizers()
	// create experiment (same experiment runs every iteration)
	var experiment = experiments.ExperimentBuilder("locustBatchFromNamespaces", d.Slas, d.OutputDir)

	defer d.report(optimizers)
	// do optimization for x iterations
	for currIter := 0; currIter < d.NbOfIterations; currIter++ {
		log.Printf("Decomposer: starting iteration: %v/%v", currIter+1, d.NbOfIterations)
		slasSamples := make([][]models.Config, len(d.Slas))
		slaSampleResults := make([][]models.ConfigResult, len(d.Slas))
		// get configs for each sla from optimizers
		sampleSize := 0
		for i := range d.Slas {
			configs, err := optimizers[i].GetNextConfigSamples(currIter)
			check(err)
			sampleSize = len(configs)
			slasSamples[i] = configs
			slaSampleResults[i] = make([]models.ConfigResult, sampleSize)
		}
		// for each sample in the iteration
		for sampleNb := 0; sampleNb < sampleSize; sampleNb++ {
			log.Printf("\tSample: %v/%v", sampleNb+1, sampleSize)
			(*experiment).SetIterationAndSample(currIter, sampleNb)
			//create a benchmark
			currBench := bench.Bench{}
			currBench.AddExperiment(*experiment)
			//match configs and charts to sla namespaces
			for slaNb, sla := range d.Slas {
				chart, err := d.getChart(sla.ChartName)
				check(err)
				config := slasSamples[slaNb][sampleNb]
				currBench.AddNamespace(bench.CreateNamespace(sla.Name, chart, config))
			}
			// execute the benchmark
			log.Printf("\t\tBenchmarking sample: %v/%v", sampleNb+1, sampleSize)
			result := d.executeBench(currBench)

			// extract Experiment results for each SLA from experimentResult
			log.Printf("\t\tProcessing results of sample: %v/%v", sampleNb+1, sampleSize)
			for slaNb, sla := range d.Slas {
				config := slasSamples[slaNb][sampleNb]
				slaResult := result.GetResultForSLA(sla)
				slaSampleResults[slaNb][sampleNb] = models.CreateConfigResult(&config, slaResult)
			}

		}

		// add configuration results to optimizers
		for slaNb, _ := range d.Slas {
			configResults := slaSampleResults[slaNb]
			optimizers[slaNb].AddConfigResults(currIter, configResults)
			if currIter == (d.NbOfIterations - 1) {
				optimizers[slaNb].GetNextConfigSamples(d.NbOfIterations)
			}
		}
	}

}

func (d *Decomposer) report(optimizers []optimizers.Optimizer) {
	filepath := d.OutputDir + "report.csv"
	log.Printf("writing report to %v...", filepath)
	//REPORT
	report := "\n\n\n\n\n"
	for i := range optimizers {
		optReport := fmt.Sprintf("REPORT optimizer %v :\n%v \n\n\n", i, optimizers[i].Report())
		report += optReport
	}
	utils.CreateDirWithNecessaryParentsIfnotExists(d.OutputDir)
	utils.WriteStringToFile(filepath, report)
	log.Printf("%v", report)
}

func (d *Decomposer) employNameSpaceStrategy() {
	if d.NamespaceStrategy == "NSPT" {
		log.Fatal("Decomposer: employNameSpaceStrategy: NSPT not yet supported")
	} else {
		return
	}
}

func (d *Decomposer) initializeOptimizers() []optimizers.Optimizer {
	opts := make([]optimizers.Optimizer, len(d.Slas))
	var err error
	for i, sla := range d.Slas {
		opts[i], err = optimizers.InitializeOptimizer(d.Optimizer, sla, d.NbOfIterations, d.NbOfSamplesPerIteration)
		opts[i].SetUtilityFunction(utilityfunc.InitializeUtilityFunc(d.UtilFunc))
		check(err)
	}
	return opts
}

func (d *Decomposer) executeBench(b bench.Bench) models.ExperimentResult {
	// check if executed before
	if found, result := d.benchPreviouslyExecuted(b); found {
		log.Printf("\t\t Found same previously executed benchmark, returning cached results.")
		return result.Result
	}
	if d.offline {
		log.Panicf("Decomposer: set to offline result is not found in given dataset.")
	}
	result := b.Execute()
	d.BenchResults = append(d.BenchResults, BenchResult{b, result})
	d.saveResultsJSON(d.resultFilePath())
	return result
}

func (d *Decomposer) benchPreviouslyExecuted(b bench.Bench) (found bool, result BenchResult) {
	for _, prevB := range d.BenchResults {
		if prevB.Bench.Equal(&b) {
			return true, prevB
		}
	}
	return false, result
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func (d *Decomposer) getChart(name string) (models.Chart, error) {
	for _, c := range d.Charts {
		if c.Name == name {
			return c, nil
		}
	}
	return models.Chart{}, errors.New("Decomposer: unable to find chart " + name)
}

func (d *Decomposer) resultFilePath() string {
	if !strings.HasSuffix(d.OutputDir, "/") {
		d.OutputDir = d.OutputDir + "/"
	}
	return d.OutputDir + "results.json"
}

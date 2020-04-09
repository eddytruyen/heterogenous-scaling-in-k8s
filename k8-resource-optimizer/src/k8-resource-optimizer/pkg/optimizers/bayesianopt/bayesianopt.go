package bayesianopt

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os/exec"

	"k8-resource-optimizer/pkg/optimizers/bestconfig"

	"k8-resource-optimizer/pkg/utils"

	"k8-resource-optimizer/pkg/models"
	"k8-resource-optimizer/pkg/optimizers/utilityfunc"
)

const workDir = "/tmp/bayesianopt/"
const plotsDir = "/tmp/bayesianopt/plots/"
const inputPathCreation = "/tmp/bayesianopt/iter-%v.in.json"                  //%v is replaced by current iter
const outputPathCreation = "/tmp/bayesianopt/iter-%v.out.json"                //%v is replaced by current iter
const outputPathPlotCreation = "/tmp/bayesianopt/plots/iter-%v.aquistion.pdf" //%v is replaced by current iter

type BayesianOpt struct {
	settings                settings
	sla                     models.SLA
	nbOfiterations          int
	nbOfSamplesPerIteration int
	utiltfunc               utilityfunc.UtilityFunc
	results                 []models.ConfigResult
	plotPaths               []string
}

type Domain struct {
	Name       string `json:"name"`
	TypeDomain string `json:"type"`
	Domain     []int  `json:"domain"`
}

type settings struct {
	Domain       []Domain        `json:"domain"`
	DomainValues [][]interface{} `json:"domainValues"`
	Scores       [][]float64     `json:"scores"`
	ExactEval    bool            `json:"exact_eval"`
}

type parameterSuggestion struct {
	Name  string `json:"name"`
	Value int    `json:"value"`
}

func CreateBayesianOptimzer(sla models.SLA, nbOfiterations int, nbOfSamplesPerIteration int) *BayesianOpt {
	bopt := BayesianOpt{}
	bopt.settings.ExactEval = true
	bopt.nbOfiterations = nbOfiterations
	bopt.nbOfSamplesPerIteration = nbOfSamplesPerIteration
	bopt.settings.Domain = []Domain{}
	bopt.results = []models.ConfigResult{}
	bopt.settings.Scores = [][]float64{}
	bopt.settings.DomainValues = [][]interface{}{}
	bopt.sla = sla
	for _, par := range sla.Parameters {

		bopt.addDomain(parameterToDiscreteDomain(par))

	}
	return &bopt
}

func (bopt *BayesianOpt) GetNextConfigSamples(iteration int) ([]models.Config, error) {
	var out []models.Config
	if iteration == 0 {
		out, err := bopt.createInitialSamples()

		return out, err
	}
	utils.CreateDirWithNecessaryParentsIfnotExists(plotsDir)
	bopt.writeSettingsToJSON(iteration)
	args := []string{
		"bayesianoptimization/gpyopt_script.py",
		fmt.Sprintf(inputPathCreation, iteration),
		fmt.Sprintf(outputPathCreation, iteration),
		fmt.Sprintf(outputPathPlotCreation, iteration),
	}

	res, err := exec.Command("python", args...).Output()
	if err != nil {
		log.Panicf("BayesianOptimizer: error in executing bayesian optimization python script: executing command: %v %v, %v", args, err, res)
		return nil, err
	}

	//read suggestion form output file

	out, err = bopt.readSuggestionFromJSON(iteration)

	if err != nil {
		return nil, err
	}

	return out, nil

}

func (bopt *BayesianOpt) createInitialSamples() ([]models.Config, error) {
	bestconfig := bestconfig.CreateBestConfigOptimzer(bopt.sla, 1, bopt.nbOfSamplesPerIteration)
	return bestconfig.GetNextConfigSamples(0)
}
func (bopt *BayesianOpt) AddConfigResults(iteration int, results []models.ConfigResult) error {
	// REPORT
	report := "\nconfigs"
	bopt.addConfigResults(results...)
	report += bopt.sla.ReportParametersHeader() + "\tscore\n"
	for i, result := range results {
		score, err := bopt.utiltfunc(bopt.sla, &result)
		if err != nil {
			return err
		}
		bopt.addDomainValue(configToDomainValue(*result.GetConfig()))
		bopt.addScore(score)
		_, data := result.GetConfig().Report()
		report += fmt.Sprintf("%v\t%v\t%v\n", i, data, score)
	}
	log.Printf("%v", report)

	return nil
}

func configToDomainValue(conf models.Config) []interface{} {

	out := make([]interface{}, len(conf.GetParameterSettings()))
	for i, ps := range conf.GetParameterSettings() {

		out[i] = ps.GetValue().GetValue()

	}
	return out
}

func (bopt *BayesianOpt) SetUtilityFunction(utilfunc utilityfunc.UtilityFunc) {
	bopt.utiltfunc = utilfunc
}

func (bopt *BayesianOpt) writeSettingsToJSON(iter int) {
	utils.CreateDirWithNecessaryParentsIfnotExists(workDir)
	err := utils.WriteObjectToJSONFile(fmt.Sprintf(inputPathCreation, iter), bopt.settings)
	if err != nil {
		log.Fatal("BayesianOptimizer: unable to write settings to file")
	}
}

func (bopt *BayesianOpt) readSuggestionFromJSON(iter int) ([]models.Config, error) {
	path := fmt.Sprintf(outputPathCreation, iter)
	//read file
	raw, err := ioutil.ReadFile(path)
	if err != nil {
		log.Printf("Decomposer: readSuggestionFromJSON: Error reading suggestion: %v", err)
		return nil, err
	}
	//parse byte to suggestions
	var suggestions []parameterSuggestion
	err = json.Unmarshal(raw, &suggestions)
	if err != nil {
		log.Printf("Decomposer: readSuggestionFromJSON: Error parsing suggestions: %v", err)
		return nil, err
	}
	out := []models.Config{}
	conf := models.Config{}
	//convert suggestion to config
	for _, suggestion := range suggestions {
		parameter, err := bopt.sla.GetParameter(suggestion.Name)
		if err != nil {
			log.Printf("Decomposer: readSuggestionFromJSON: suggestion does not contain parameter: %v", err)
			return nil, err
		}
		// value, ok := strconv.Atoi(suggestion.Value)
		// if ok != nil {
		// 	log.Printf("Decomposer: readSuggestionFromJSON: unable to parse suggestion value to int %v", suggestion.Value)
		// 	return nil, errors.New("Decomposer: readSuggestionFromJSON: unable to parse suggestion value to int")
		// }

		valuePar := models.ParameterValueInt{Value: suggestion.Value, Type: "int"}

		ps := models.ParameterSetting{Parameter: parameter, Value: valuePar}
		conf.AddParameterSetting(ps)

	}
	out = append(out, conf)

	return out, nil

}

func parameterToDiscreteDomain(par models.Parameter) Domain {
	out := Domain{}
	out.Name = par.Name
	out.TypeDomain = "discrete"
	for _, pv := range par.Searchspace.EnumarateSampleSearchSpace() {
		value, ok := pv.(models.ParameterValueInt)
		if !ok {
			log.Fatal("BayesianOptimizer: error in casting valueParameter to ValueParameterInt")
		}
		out.Domain = append(out.Domain, value.Value)
	}
	return out
}

func parameterToContiniousDomain(par models.Parameter) Domain {
	out := Domain{}
	out.Name = par.Name
	out.TypeDomain = "continuous"
	out.Domain = append(out.Domain, par.Searchspace.Min)
	out.Domain = append(out.Domain, par.Searchspace.Max)
	// for _, pv := range par.Searchspace.EnumarateSampleSearchSpace() {
	// 	value, ok := pv.(models.ParameterValueInt)
	// 	if !ok {
	// 		log.Fatal("BayesianOptimizer: error in casting valueParameter to ValueParameterInt")
	// 	}
	// 	out.Domain = append(out.Domain, value.Value)
	// }
	return out
}

func (bopt *BayesianOpt) addDomain(newDomain Domain) {
	bopt.settings.Domain = append(bopt.settings.Domain, newDomain)
}

func (bopt *BayesianOpt) addDomainValue(domainValue []interface{}) {
	bopt.settings.DomainValues = append(bopt.settings.DomainValues, domainValue)
}

func (bopt *BayesianOpt) addScore(score float64) {
	bopt.settings.Scores = append(bopt.settings.Scores, []float64{score})
}

func (bopt *BayesianOpt) addConfigResults(crs ...models.ConfigResult) {
	bopt.results = append(bopt.results, crs...)
}

func (bopt *BayesianOpt) Report() string {
	// bestscore := 0
	header := ""
	data := ""
	for i, cr := range bopt.results {
		headerConfig, dataConfig := cr.GetConfig().Report()
		headerExperiment, dataExperimnent := cr.GetExperimentResult().Report(bopt.sla)
		if i == 0 {
			header += fmt.Sprintf("%v\t%v\t%v\t%v\n", "config #", headerConfig, "score", headerExperiment)
		}
		if i < len(bopt.settings.Scores) {
			data += fmt.Sprintf("%v\t%v\t%v\t%v\n", i, dataConfig, bopt.settings.Scores[i][0], dataExperimnent)
		}

	}

	return header + data
}

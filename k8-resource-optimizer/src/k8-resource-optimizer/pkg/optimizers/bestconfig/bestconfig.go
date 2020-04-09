package bestconfig

import (
	"errors"
	"fmt"
	"log"
	"strconv"

	"k8-resource-optimizer/pkg/models"
	"k8-resource-optimizer/pkg/optimizers/utilityfunc"
)

// Implements a optimizer:
// Public functions to be used:
// setSLA, getNextConfigSample, getIntialSamples, addConfigResults

// What are in a Iteration? x sample configurations
// for each parameter pick x settings in searchspace
// create x Config combinations
// return configs
// add config results
// pick config with best result --> update searchspace for each parameter

const IterationAttempts = 200
const ShuffleAttempts = 20
const logPrefix = "\t\t"

type BestConfigOptimizer struct {
	sla                 models.SLA
	parameters          []models.Parameter
	iterations          []*iteration
	samplesPerIteration int
	utilityFunction     utilityfunc.UtilityFunc
	currentBestScore    float64
}

type iteration struct {
	Parameters   []*parameterIteration
	configs      []models.Config
	results      []models.ConfigResult
	configScores []float64
	nb           int
	backtrackTo  int
}

type parameterIteration struct {
	searchspace models.Searchspace
	Samples     []models.ParameterValue
	Parameter   *models.Parameter
}

func CreateBestConfigOptimzer(s models.SLA, nbOfIterations int, samplesPerIteration int) *BestConfigOptimizer {
	bcopt := BestConfigOptimizer{}
	bcopt.samplesPerIteration = samplesPerIteration
	bcopt.sla = s
	bcopt.currentBestScore = 0.0
	// copy parameters
	log.Printf("BestConfig: initializing with %v parameters", len(s.Parameters))
	bcopt.parameters = make([]models.Parameter, len(s.Parameters))
	copy(bcopt.parameters, s.Parameters)
	// iterations
	bcopt.iterations = []*iteration{}
	return &bcopt
}

func (bcopt *BestConfigOptimizer) getIteration(iternb int) (*iteration, error) {
	if len(bcopt.iterations) >= iternb+1 {
		return bcopt.iterations[iternb], nil
	}
	return nil, errors.New(fmt.Sprintf("Iteration not found, request %v length %v", iternb, len(bcopt.iterations)))
}

func (bcopt *BestConfigOptimizer) createInitialIteration() (*iteration, error) {
	iter := iteration{}
	iter.nb = 0
	iter.backtrackTo = 0
	for i, p := range bcopt.parameters {
		parIter := parameterIteration{}
		parIter.Parameter = &bcopt.parameters[i]
		iter.Parameters = append(iter.Parameters, &parIter)
		parIter.searchspace.Max = p.Searchspace.Max
		parIter.searchspace.Min = p.Searchspace.Min
		parIter.searchspace.Granularity = p.Searchspace.Granularity
	}
	return &iter, nil
}

func (bcopt *BestConfigOptimizer) createNextIterationWithSearchspacesBasedOnPrevIter(iter *iteration, nb int) (*iteration, error) {
	var ret iteration
	ret = iteration{}
	ret.nb = nb
	if iter == nil || len(iter.configs) == 0 || len(iter.results) != len(iter.configs) {
		return nil, errors.New("Previous iterations has no configs or no results")
	}
	bestConfig, bestScore, err := bcopt.getBestConfig(iter)

	if err != nil {
		return nil, err
	}

	//check if backtrack
	if bestScore > bcopt.currentBestScore {
		// if backtrack
		// new iter to base searchspace on
		log.Printf("%vBestConfig: Backtracking to searchspace of iter: %v", logPrefix, iter.backtrackTo)
		iter, err = bcopt.getIteration(iter.backtrackTo)
		if err != nil {
			return nil, fmt.Errorf("unable to backtrack to iteration number: %v", iter.backtrackTo)
		}
		// set backtrack to backtrack of new
		ret.backtrackTo = iter.backtrackTo
		//copy parameters and seachspaces
		for _, pi := range iter.Parameters {
			newPi := parameterIteration{}
			newPi.Parameter = pi.Parameter
			newPi.searchspace = pi.searchspace
			ret.Parameters = append(ret.Parameters, &newPi)
		}

	} else {
		// if not backtrack set prev as new backtrack
		ret.backtrackTo = iter.nb
		for _, pi := range iter.Parameters {
			newPi := parameterIteration{}
			newPi.Parameter = pi.Parameter
			ps, err := bestConfig.GetParameterSetting(pi.Parameter.Name)
			if err != nil {
				return nil, err
			}
			newPi.searchspace, err = pi.recursiveBoundAndSearch(ps)
			if err != nil {
				return nil, err
			}
			ret.Parameters = append(ret.Parameters, &newPi)
		}
	}

	return &ret, nil
}

func (bcopt *BestConfigOptimizer) getBestConfig(iter *iteration) (out *models.Config, score float64, err error) {

	if len(iter.results) == 0 || len(iter.configScores) != len(iter.results) {
		return out, -1.0, errors.New("No best config found of iteration: " + strconv.Itoa(iter.nb))
	}

	bestIndex := 0
	for i := 1; i < len(iter.configScores); i++ {
		if iter.configScores[bestIndex] > iter.configScores[i] {
			bestIndex = i
		}
	}
	return &iter.configs[bestIndex], iter.configScores[bestIndex], nil
}

func (bcopt *BestConfigOptimizer) calculateScoresAndGetBest(iter *iteration) (*models.Config, float64, error) {

	if len(iter.results) == 0 {
		return nil, -1.0, errors.New("No best config found of iteration: " + strconv.Itoa(iter.nb))
	}
	iter.configScores = make([]float64, len(iter.results))
	bestConfigResult := &iter.results[0]
	bestScore, err := bcopt.utilityFunction(bcopt.sla, bestConfigResult)
	if err != nil {
		return nil, -1.0, err
	}
	iter.configScores[0] = bestScore
	bestConfigNb := 0
	for i := 1; i < len(iter.results); i++ {
		score, err := bcopt.utilityFunction(bcopt.sla, &iter.results[i])
		if err != nil {
			return nil, -1.0, err
		}
		iter.configScores[i] = score
		if score < bestScore {
			bestScore = score
			bestConfigResult = &iter.results[i]
			bestConfigNb = i
		}
	}

	if bestScore < bcopt.currentBestScore {
		bcopt.currentBestScore = bestScore
	}

	log.Printf("%v\n==> selected config %v as best score: %v current best is %v:", bcopt.reportOnIterationResults(iter), bestConfigNb, bestScore, bcopt.currentBestScore)

	return bestConfigResult.GetConfig(), bestScore, nil

}

func (iter *iteration) generateParameterSamples(nb int) {
	// Generate samples for each parameter using DDS (Devide and diverge sampling), shuffle
	if iter.Parameters == nil {
		log.Panicf("BestConfig: iteration has no parameter array initialized")
	}
	for _, parIter := range iter.Parameters {
		if parIter == nil {
			log.Panicf("BestConfig: iteration has  parameter with value nil")
		}
		samples, _ := parIter.searchspace.CreateSamples(nb)
		parIter.Samples = samples
		parIter.shuffle()
	}

}

func (iter *iteration) composeConfigsFromSamples(nb int) {
	iter.configs = make([]models.Config, nb)
	for i := 0; i < nb; i++ {
		iter.configs[i] = iter.composeConfigFromSample(i)
	}
}

func (iter *iteration) composeConfigFromSample(nr int) models.Config {
	out := models.Config{}
	for _, pi := range iter.Parameters {
		out.AddParameterSetting(models.ParameterSetting{pi.Parameter, pi.Samples[nr]})
	}
	return out
}

// NOTE SEARCHSPACE includes borders (min,max)
// exclude should include values already taken in the interval (min, max)

func (bcopt *BestConfigOptimizer) configsTestedInPrevIterationsBefore(before int, cs []models.Config) (bool, error) {
	if before == 0 {
		return false, nil
	}
	if len(bcopt.iterations) < before-1 {
		return false, errors.New("iteration uniqueness check request on future")
	}
	for _, c := range cs {
		for i := 0; i < before; i++ {
			if bcopt.iterations[i].containsConfig(c) {
				return true, nil
			}
		}
	}

	return false, nil
}

func (bcopt *BestConfigOptimizer) GetNextConfigSamples(iternb int) ([]models.Config, error) {
	iter, err := bcopt.getIteration(iternb)
	if err == nil {
		return iter.configs, nil
	} else if iternb == 0 {
		// initialize new iteration (with searchspaces) based on previous
		iter, err = bcopt.createInitialIteration()
	} else if prevIter, err2 := bcopt.getIteration((iternb - 1)); err2 == nil {

		iter, err = bcopt.createNextIterationWithSearchspacesBasedOnPrevIter(prevIter, iternb)
		// initialize new iteration (with searchspaces) based on previous
	} else {
		return []models.Config{}, errors.New("Previous iteration not found")

	}
	if err != nil {
		log.Panicf("Bestconfig error in getting nex configsample for iteration %v error: %v", iternb, err)
	}
	bcopt.iterations = append(bcopt.iterations, iter)

	return bcopt.generateConfigs(iternb)

}

// Generate samples in iteration @iterationNb, assuming that searchparameters have been set for the iteration based
// on the results of the previous iteration.
func (bcopt *BestConfigOptimizer) generateConfigs(iterationNb int) ([]models.Config, error) {
	iter := bcopt.iterations[iterationNb]
	if iter == nil {
		log.Panicf("BestConfig: accessing iteration with value nil")
	}
	for i := 0; i < IterationAttempts; i++ {
		iter.generateParameterSamples(bcopt.samplesPerIteration)
		iter.composeConfigsFromSamples(bcopt.samplesPerIteration)

		notunique, err := bcopt.configsTestedInPrevIterationsBefore(iterationNb, iter.configs)
		if err != nil {
			return nil, err
		}
		j := 0
		for notunique && j < ShuffleAttempts {
			iter.shuffle()
			j++
			notunique, err = bcopt.configsTestedInPrevIterationsBefore(iterationNb, iter.configs)
		}
		if !notunique {
			log.Printf("%v", bcopt.reportOnIterationSampleSelection(iter))
			return iter.configs, nil
		}

	}
	return []models.Config{}, errors.New("Unable to generate unique untested configs for iteration: " + strconv.Itoa(iterationNb))

}

func (bcopt *BestConfigOptimizer) AddConfigResults(iterationNb int, results []models.ConfigResult) error {
	iter, err := bcopt.getIteration(iterationNb)
	if err != nil {
		log.Print("BestConfig Optimizer: AddConfigResults: adding results to uniniated iteation")
		return err
	}
	iter.results = append(iter.results, results...)
	bcopt.calculateScoresAndGetBest(iter)
	return nil

}

func (pi *parameterIteration) recursiveBoundAndSearch(best models.ParameterSetting) (models.Searchspace, error) {
	out := models.Searchspace{}
	out.Granularity = pi.searchspace.Granularity
	bestValue := best.GetValue()
	var min, max models.ParameterValue
	min = models.ParameterValueInt{Value: pi.searchspace.Min, Type: "int"}
	max = models.ParameterValueInt{Value: pi.searchspace.Max, Type: "int"}
	for i := 0; i < len(pi.Samples); i++ {
		// log.Printf("comparing best %v min: %v max %v curr: %v, %v, %v, %v, %v", bestValue.String(), min.String(), max.String(), pi.Samples[i].String(), pi.Samples[i].Less(bestValue), pi.Samples[i].Greater(min), pi.Samples[i].Greater(bestValue), pi.Samples[i].Less(max))
		if pi.Samples[i].Less(bestValue) && pi.Samples[i].Greater(min) {
			min = pi.Samples[i]
		} else if pi.Samples[i].Greater(bestValue) && pi.Samples[i].Less(max) {
			max = pi.Samples[i]
		}
	}
	temp, err := strconv.Atoi(min.String())
	if err != nil {
		return out, errors.New("Unable to cast parameterValue to int")
	}
	out.Min = temp
	temp, err = strconv.Atoi(max.String())
	if err != nil {
		return out, errors.New("Unable to cast parameterValue to int")
	}
	out.Max = temp

	return out, nil
}

// SMALL HELPFUL FUCTION
func (iter *iteration) shuffle() {
	for _, pi := range iter.Parameters {
		pi.shuffle()
	}
}
func (pi *parameterIteration) shuffle() {
	pi.Samples = models.ShuffleParameterValue(pi.Samples)
}

func (iter *iteration) containsConfig(c models.Config) bool {
	return c.PartOf(iter.configs)
}

func (bcopt *BestConfigOptimizer) SetUtilityFunction(utilityFunc utilityfunc.UtilityFunc) {
	bcopt.utilityFunction = utilityFunc
}

// REPORT
func (bcopt *BestConfigOptimizer) reportOnIterationResults(iter *iteration) string {
	header := "\nconfigs\t"
	data := ""
	for i, config := range iter.configs {
		confheader, confdata := config.Report()
		if i == 0 {
			header += confheader + "\tscore\n"
		}
		data += fmt.Sprintf("%v\t%v\t%v\n", i, confdata, iter.configScores[i])
	}
	return header + data
}

func (bcopt *BestConfigOptimizer) reportOnIterationSampleSelection(iter *iteration) string {
	report := "\nPar\t\tmin\tmax\tselected"

	for _, par := range iter.Parameters {
		report += fmt.Sprintf("\n%v\t%v\t%v", par.Parameter.Name, par.searchspace.Min, par.searchspace.Max)
		for _, s := range par.Samples {
			report += fmt.Sprintf("\t%v", s.String())
		}
		report += "\n"
	}
	report += "\nconfigs"
	report += bcopt.sla.ReportParametersHeader() + "\n"
	for i, config := range iter.configs {
		_, confdata := config.Report()
		report += fmt.Sprintf("%v\t%v\n", i, confdata)
	}
	return report
}

func (bcopt *BestConfigOptimizer) Report() string {
	header := ""
	data := ""
	for i, iter := range bcopt.iterations {
		for j, cr := range iter.results {
			headerConfig, dataConfig := cr.GetConfig().Report()
			headerExperiment, dataExperimnent := cr.GetExperimentResult().Report(bcopt.sla)
			if i == 0 && j == 0 {
				header += fmt.Sprintf("%v\t%v\t%v\t%v\n", "config #", headerConfig, "score", headerExperiment)
			}
			score, err := bcopt.utilityFunction(bcopt.sla, &cr)
			if err != nil {
				log.Panic(err)
			}
			data += fmt.Sprintf("%v\t%v\t%v\t%v\n", (i*len(iter.results))+j, dataConfig, score, dataExperimnent)
		}
	}
	return header + data
}
